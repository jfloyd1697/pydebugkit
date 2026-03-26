from pyqtgraph import PlotWidget, mkPen

from pydebugkit.core.registry import registry


class LivePlot:
    """Handles multiple series in a plot with per-key updates."""
    def __init__(self, parent=None, title=""):
        self.plot_widget = PlotWidget(parent)
        self.plot_widget.setTitle(title)
        self.plot_widget.addLegend()
        self.curves = {}  # key -> plot curve
        self.data = {}    # key -> list of values

    def add_series(self, key, **kwargs):
        """Add a series. kwargs are passed to mkPen and plot (color, width, style)."""
        color = kwargs.pop("pen", "w")
        width = kwargs.pop("width", 1)
        pen = mkPen(color=color, width=width)
        self.curves[key] = self.plot_widget.plot([], [], name=key, pen=pen, **kwargs)
        self.data[key] = []
        registry.subscribe(key, self.update_series)

    def update_series(self, key, value, t=None):
        if key not in self.curves:
            raise KeyError(f"Series '{key}' not added to plot")

        # -------------------------
        # CASE 1: value is a full series (Recorder)
        # -------------------------
        if isinstance(value, (list, tuple)):
            y = value
            x = list(range(len(y))) if t is None else t
            self.curves[key].setData(x, y)
            return

        # -------------------------
        # CASE 2: scalar stream (normal)
        # -------------------------
        self.data[key].append(value)

        y = self.data[key]
        x = list(range(len(y))) if t is None else t

        self.curves[key].setData(x, y)