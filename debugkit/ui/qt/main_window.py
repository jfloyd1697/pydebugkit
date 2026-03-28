from PyQt5.QtWidgets import (
    QMainWindow, QDockWidget, QAction, QFileDialog, QStatusBar
)
from PyQt5.QtCore import QTimer, Qt
import os
from datetime import datetime

from debugkit.core import Registry, Recorder
from debugkit.ui.persistence import AppState, AppSettings, PersistenceManager
from debugkit.ui.qt.inspector_panel import InspectorPanel
from debugkit.ui.qt.plot_manager import MultiPanelPlotManager
from debugkit.ui.qt.recorder_control import RecorderControl
from debugkit.ui.qt.settings_window import SettingsWindow


class DebugMainWindow(QMainWindow):
    def __init__(self, registry: Registry, settings: AppSettings, parent=None):
        super().__init__(parent)
        self.registry = registry
        self.settings = settings

        # Core UI components
        self.persistence = PersistenceManager()
        self.recorder = RecorderControl()
        self.recorder.set_recorder(Recorder(registry))

        self.plot_manager = MultiPanelPlotManager(self.layout())
        self.inspector_panel = InspectorPanel(registry=self.registry, plot_manager=self.plot_manager)
        self.settings_window = SettingsWindow(settings=self.settings, on_update=self.update_autosave_timer)

        self.docks = {}

        self.setWindowTitle("DebugKit")
        self.resize(1200, 800)

        # Status bar
        self.status = QStatusBar()
        self.setStatusBar(self.status)

        # Dock inspector
        self.add_dock_widget("Inspector", self.inspector_panel, Qt.LeftDockWidgetArea)

        # Menu
        self.menu_bar = self.menuBar()
        self.setup_file_menu()

        # Autosave timer
        self.autosave_timer = QTimer(self)
        self.autosave_timer.timeout.connect(self.auto_save)
        self.update_autosave_timer()

        # Pause flag
        self.paused = False

    # -------------------------------
    # Dock management
    # -------------------------------
    def add_dock_widget(self, title, widget, area):
        dock = QDockWidget(title, self)
        dock.setWidget(widget)
        dock.setObjectName(title)
        self.addDockWidget(area, dock)
        self.docks[title] = dock
        return dock

    def add_plot_widget(self, widget, name="Plot"):
        self.add_dock_widget(name, widget, Qt.RightDockWidgetArea)

    # -------------------------------
    # Menu
    # -------------------------------
    def setup_file_menu(self):
        file_menu = self.menu_bar.addMenu("File")

        new_action = QAction("New", self)
        new_action.triggered.connect(self.new_session)
        file_menu.addAction(new_action)

        open_action = QAction("Open...", self)
        open_action.triggered.connect(self.open_session)
        file_menu.addAction(open_action)

        save_action = QAction("Save", self)
        save_action.triggered.connect(self.save_session_action)
        file_menu.addAction(save_action)

        save_as_action = QAction("Save As...", self)
        save_as_action.triggered.connect(self.save_as_session)
        file_menu.addAction(save_as_action)

        self.recent_menu = file_menu.addMenu("Recent Sessions")
        self.update_recent_sessions_menu()

        settings_action = QAction("Settings...", self)
        settings_action.triggered.connect(self.open_settings_window)
        file_menu.addAction(settings_action)

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    # -------------------------------
    # Session management
    # -------------------------------
    def new_session(self):
        self.registry._settings.clear()
        for dock in self.docks.values():
            dock.widget().clear()
        self.status.showMessage("New session started", 3000)

    def open_session(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open Session", "", "DebugKit Session (*.dks)")
        if filename:
            self.load(filename)

    def save_session_action(self):
        if hasattr(self, "_current_file") and self._current_file:
            self.save_session(self._current_file)
        else:
            self.save_as_session()

    def save_as_session(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save Session As", "", "DebugKit Session (*.dks)")
        if filename:
            if not filename.endswith(".dks"):
                filename += ".dks"
            self._current_file = filename
            self.save_session(filename)

    def save_session(self, filename):
        self.save(filename)
        self.status.showMessage(f"Session saved to {filename}", 3000)
        self.update_recent_sessions(filename)

    # -------------------------------
    # Save State
    # -------------------------------
    def build_state(self):
        return AppState(
            inspector=self.inspector_panel.to_config(),
            plots=self.plot_manager.to_config(),
            recorder=self.recorder.to_config(),
            settings=AppSettings(
                autosave_enabled=True,
                autosave_interval_sec=10
            )
        )

    def apply_state(self, state: AppState):
        self.inspector_panel.from_config(state.inspector)
        self.plot_manager.from_config(state.plots)
        self.recorder.from_config(state.recorder)

    # -------------------------------
    # File Actions
    # -------------------------------
    def save(self, filepath):
        state = self.build_state()
        self.persistence.save(state, filepath)

    def load(self, filepath):
        state = self.persistence.load(filepath)
        self.apply_state(state)

    # -------------------------------
    # Recent sessions
    # -------------------------------
    def update_recent_sessions(self, path):
        recent = getattr(self.settings, "recent_sessions", [])
        if path in recent:
            recent.remove(path)
        recent.insert(0, path)
        self.settings.recent_sessions = recent[:10]
        self.update_recent_sessions_menu()

    def update_recent_sessions_menu(self):
        self.recent_menu.clear()
        for path in getattr(self.settings, "recent_sessions", []):
            act = QAction(path, self)
            act.triggered.connect(lambda checked, p=path: self.load_session(p))
            self.recent_menu.addAction(act)

    def load_session(self, path):
        if os.path.exists(path):
            with open(path, "r") as f:
                state = AppState.from_json(f.read())
                self.apply_state(state)
            self.status.showMessage(f"Session loaded from {path}", 3000)

    # -------------------------------
    # Settings window
    # -------------------------------
    def open_settings_window(self):
        self.settings_window.show()
        self.settings_window.raise_()

    # -------------------------------
    # Autosave
    # -------------------------------
    def update_autosave_timer(self):
        interval_ms = int(self.settings.autosave_interval_sec * 1000)
        if self.settings.autosave_enabled:
            self.autosave_timer.start(interval_ms)
        else:
            self.autosave_timer.stop()

    def auto_save(self):
        if hasattr(self, "_current_file") and self._current_file:
            self.save_session(self._current_file)
            timestamp = datetime.now().strftime('%H:%M:%S')
            self.settings_window.update_last_save(timestamp)
            self.status.showMessage(f"Autosaved at {timestamp}", 3000)

    # -------------------------------
    # Pause/Resume
    # -------------------------------
    def toggle_pause(self):
        self.paused = not self.paused
        msg = "Paused" if self.paused else "Resumed"
        self.status.showMessage(msg, 3000)
