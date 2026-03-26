# main_window.py
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget

class DebugMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DebugKit")
        self.central = QWidget()
        self.setCentralWidget(self.central)
        self.layout = QVBoxLayout()
        self.central.setLayout(self.layout)

    def add_plot_widget(self, widget):
        """Add a plot widget to the main window layout."""
        self.layout.addWidget(widget)

    def save_layout(self, path):
        state = self.saveState().data()
        with open(path, "wb") as f:
            f.write(state)

    def load_layout(self, path):
        with open(path, "rb") as f:
            state = f.read()
            self.restoreState(state)
