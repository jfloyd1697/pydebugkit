from PyQt5.QtWidgets import QWidget, QVBoxLayout
import pyqtgraph as pg
from collections import defaultdict

from debugkit.ui.persistence.settings import PlotSeriesConfig, PlotPanelConfig


class PlotPanel(QWidget):
    """Single panel with multiple series"""
    def __init__(self, title="Plot Panel"):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.plot_widget = pg.PlotWidget(title=title)
        self.layout.addWidget(self.plot_widget)

        self.curves = {}        # key -> curve
        self.units_map = {}     # key -> units
        self.timestamps = defaultdict(list)  # key -> timestamps
        self.data = defaultdict(list)        # key -> values

        self.plot_widget.addLegend()

    def add_series(self, key, initial=None, **kwargs):
        if key in self.curves:
            return
        curve = self.plot_widget.plot(
            name=key,
            pen=kwargs.get("pen", None),
            symbol=kwargs.get("symbol", None),
            symbolBrush=kwargs.get("symbolBrush", None)
        )
        self.curves[key] = curve
        self.units_map[key] = kwargs.get("units", "")
        if initial is not None:
            self.update_series(key, [0], [initial])

    def remove_series(self, key):
        if key in self.curves:
            self.plot_widget.removeItem(self.curves[key])
            del self.curves[key]
            del self.units_map[key]
            if key in self.data:
                del self.data[key]
            if key in self.timestamps:
                del self.timestamps[key]

    def update_series(self, key, x, y):
        """Update series data"""
        if key not in self.curves:
            return
        self.timestamps[key] = x
        self.data[key] = y
        self.curves[key].setData(x, y)


class MultiPanelPlotManager:
    """
    Manages multiple plot panels.
    Supports adding/removing series and updating them dynamically.
    """
    def __init__(self, parent_layout):
        self.parent_layout = parent_layout  # QVBoxLayout or other layout
        self.panels = {}
        self.key_to_panel = {}

    def create_panel(self, name):
        panel = PlotPanel(title=name)
        self.parent_layout.add_plot_widget(panel, name=name)
        self.panels[name] = panel
        return panel

    def add_series(self, key, initial=None, units=None, **kwargs):
        """Add series to default or first panel"""
        if key in self.key_to_panel:
            panel = self.key_to_panel[key]
        else:
            # Default: first panel
            panel = next(iter(self.panels.values()))
            self.key_to_panel[key] = panel

        plot_kwargs = kwargs.copy()
        if units:
            plot_kwargs["units"] = units
        panel.add_series(key, initial=initial, **plot_kwargs)

    def remove_series(self, key):
        if key in self.key_to_panel:
            panel = self.key_to_panel[key]
            panel.remove_series(key)
            del self.key_to_panel[key]

    def update_series(self, key, x, y):
        if key in self.key_to_panel:
            panel = self.key_to_panel[key]
            panel.update_series(key, x, y)

    def to_config(self):
        panels = []
        for name, panel in self.panels.items():
            series = []
            for key in panel.curves.keys():
                series.append(PlotSeriesConfig(key=key, panel=name))
            panels.append(PlotPanelConfig(name=name, series=series))
        return panels


    def from_config(self, configs: list[PlotPanelConfig]):
        for panel_cfg in configs:
            panel = self.create_panel(panel_cfg.name)
            for series in panel_cfg.series:
                self.add_series(series.key)