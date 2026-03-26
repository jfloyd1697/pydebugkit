from .main_window import DebugMainWindow
from .plotter import LivePlot

class MultiPlotManager:
    """Manages multiple panels with multiple LivePlots."""
    def __init__(self, main_window: DebugMainWindow):
        self.main_window = main_window
        self.panels = {}

    def create_panel(self, title):
        plot = LivePlot(parent=self.main_window, title=title)
        self.panels[title] = plot
        self.main_window.add_plot_widget(plot.plot_widget)
        return plot