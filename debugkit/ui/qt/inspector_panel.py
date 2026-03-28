from PyQt5.QtWidgets import QWidget, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QDockWidget
from PyQt5.QtCore import Qt

from debugkit.core.registry import Registry
from debugkit.ui.persistence.settings import InspectorConfig
from debugkit.ui.qt.plot_manager import MultiPanelPlotManager


class InspectorPanel(QDockWidget):
    """
    Feature-complete Inspector Panel for DebugKit.
    - Tree-based view of properties
    - Checkboxes with tristate
    - Displays metadata
    - Live updates from Registry
    - Save/load state
    """
    def __init__(self, registry: Registry, plot_manager: MultiPanelPlotManager, parent=None):
        super().__init__("Inspector", parent)
        self.registry = registry
        self.plot_manager = plot_manager
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Signal", "Value", "Units"])
        self.tree.setColumnWidth(0, 200)
        self.tree.setColumnWidth(1, 80)
        self.tree.itemChanged.connect(self._on_item_changed)

        self.main_widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.tree)
        self.main_widget.setLayout(layout)
        self.setWidget(self.main_widget)

        self._item_map = {}  # key -> QTreeWidgetItem
        self._subscriptions = {}

    # -------------------------------
    # Tree population
    # -------------------------------
    def populate_tree(self):
        """Populate the tree with all keys from the registry"""
        self.tree.clear()
        self._item_map.clear()
        for key in self.registry.all_keys():
            prop = self.registry._settings.get(key)
            units = getattr(prop, "metadata", {}).get("units", "") if prop else ""
            value = self.registry.get(key)
            item = QTreeWidgetItem([key, str(value), units])
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(0, Qt.Unchecked)
            self.tree.addTopLevelItem(item)
            self._item_map[key] = item

            # Subscribe to live updates
            self.registry.subscribe(key, self._make_update_callback(key))

    def _make_update_callback(self, key):
        def callback(k, value):
            item = self._item_map.get(k)
            if item:
                item.setText(1, str(value))
        return callback

    # -------------------------------
    # Checkbox handling
    # -------------------------------
    def _on_item_changed(self, item, column):
        key = item.text(0)
        checked = item.checkState(0) == Qt.Checked

        if checked:
            # Add series to the plot
            value = self.registry.get(key)
            prop = self.registry._settings.get(key)
            kwargs = getattr(prop, "metadata", {}) if prop else {}
            self.plot_manager.add_series(key, initial=value, **kwargs)
        else:
            # Remove series from the plot
            self.plot_manager.remove_series(key)

    def to_config(self):
        return InspectorConfig(
            checked_keys=[
                key for key, item in self._item_map.items()
                if item.checkState(0)
            ],
            expanded_keys=[
                key for key, item in self._item_map.items()
                if item.isExpanded()
            ]
        )

    def from_config(self, config: InspectorConfig):
        for key in config.checked_keys:
            if key in self._item_map:
                self._item_map[key].setCheckState(0, Qt.Checked)

        for key in config.expanded_keys:
            if key in self._item_map:
                self._item_map[key].setExpanded(True)
