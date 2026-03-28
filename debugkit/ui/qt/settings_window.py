from PyQt5.QtWidgets import QWidget, QVBoxLayout, QCheckBox, QLabel, QPushButton, QDoubleSpinBox, QHBoxLayout

from debugkit.ui.persistence import AppSettings


class SettingsWindow(QWidget):
    def __init__(self, settings: AppSettings, on_update=None):
        super().__init__()
        self.setWindowTitle("Settings")
        self.settings = settings
        self.on_update = on_update

        layout = QVBoxLayout(self)

        self.autosave_checkbox = QCheckBox("Enable Autosave")
        self.autosave_checkbox.setChecked(settings.autosave_enabled)
        layout.addWidget(self.autosave_checkbox)

        interval_layout = QHBoxLayout()
        interval_layout.addWidget(QLabel("Autosave Interval:"))
        self.interval_spin = QDoubleSpinBox()
        self.interval_spin.setRange(1, 3600)
        self.interval_spin.setValue(settings.autosave_interval_sec)
        interval_layout.addWidget(self.interval_spin)
        layout.addLayout(interval_layout)

        self.last_save_label = QLabel("Last Auto-Save: Never")
        layout.addWidget(self.last_save_label)

        self.save_btn = QPushButton("Save Settings")
        self.save_btn.clicked.connect(self.save_settings)
        layout.addWidget(self.save_btn)

    def update_last_save(self, timestamp):
        self.last_save_label.setText(f"Last Auto-Save: {timestamp}")

    def save_settings(self):
        self.settings.autosave_enabled = self.autosave_checkbox.isChecked()
        self.settings.autosave_interval = self.interval_spin.value()
        self.settings.save()
        if self.on_update:
            self.on_update()
        self.close()