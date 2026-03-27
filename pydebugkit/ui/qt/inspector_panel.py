from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QTreeWidget, QTreeWidgetItem,
    QLabel, QSplitter
)
from PyQt5.QtCore import Qt
from pydebugkit import global_registry
from pydebugkit.ui.qt.plotter import LivePlot


class InspectorPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QHBoxLayout(self)

        splitter = QSplitter(Qt.Horizontal)

        # --- Left: Signal Tree ---
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("Signals")
        self.tree.itemChanged.connect(self._on_item_checked)

        # --- Right: Info + Plot ---
        right = QWidget()
        right_layout = QVBoxLayout(right)

        self.value_label = QLabel("Select a signal")
        self.plot = LivePlot(title="Inspector Plot")

        right_layout.addWidget(self.value_label)
        right_layout.addWidget(self.plot.plot_widget)

        splitter.addWidget(self.tree)
        splitter.addWidget(right)

        self.layout.addWidget(splitter)

        self._root_items = {}  # cache for top-level items to speed up tree population
        self._callbacks = {}  # keep track of callbacks to avoid duplicates

    # -------------------------
    # Populate Tree
    # -------------------------
    def populate_tree(self, keys):
        self.tree.clear()

        tree_data = {}

        # -------------------------
        # Build nested dict
        # -------------------------
        for key in keys:
            parts = key.split(".")
            node = tree_data

            for part in parts:
                node = node.setdefault(part, {})

            # mark leaf
            node["_key"] = key

        # -------------------------
        # Recursively build UI
        # -------------------------
        def add_items(parent, data):
            for name, subtree in sorted(data.items()):
                if name == "_key":
                    continue

                item = QTreeWidgetItem([name])
                item.setFlags(item.flags() | Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsAutoTristate)
                item.setCheckState(0, Qt.Unchecked)

                # if this node is a leaf, attach full key
                if "_key" in subtree:
                    item.setData(0, Qt.UserRole, subtree["_key"])

                if isinstance(parent, QTreeWidget):
                    parent.addTopLevelItem(item)
                else:
                    parent.addChild(item)

                add_items(item, subtree)

        add_items(self.tree, tree_data)


    # -------------------------
    # Selection
    # -------------------------
    def _on_item_checked(self, item):
        key = item.data(0, Qt.UserRole)
        checked = item.checkState(0) == Qt.Checked
        if not key:
            return

        if checked:

            time_key = tk if global_registry.has_key(tk := f"{key}_timestamps") else None

            # plot it
            self._callbacks.setdefault(key, []).extend([
                global_registry.subscribe(key, self.update_label),
                self.plot.add_series(key, time_key=time_key)
            ])

        else:
            # unsubscribe
            for cb in self._callbacks.get(key, []):
                global_registry.unsubscribe(key, cb)

            # unplot it
            if key in self.plot.curves:
                self.plot.plot_widget.removeItem(self.plot.curves[key])
                del self.plot.curves[key]
                del self.plot.data[key]

    def update_label(self, key, val):
        try:
            if isinstance(val, (list, tuple)):
                val = val[-1]
            self.value_label.setText(f"{key} = {val}")
        except Exception as e:
            self.value_label.setText(f"{key} (error)")
