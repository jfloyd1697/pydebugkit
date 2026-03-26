import sys, random, os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
from debugkit.ui.qt.main_window import DebugMainWindow
from debugkit.ui.qt.multi_plot import MultiPlotManager
from debugkit.core.registry import registry

LAYOUT_FILE = "layout.bin"

class DummyDevice:
    def __init__(self):
        self._val = 0

    @property
    def val(self):
        self._val += random.random() - 0.5
        return self._val

app = QApplication(sys.argv)
window = DebugMainWindow()
manager = MultiPlotManager(window)

# Restore layout if exists
if os.path.exists(LAYOUT_FILE):
    window.load_layout(LAYOUT_FILE)

panel1 = manager.create_panel("Panel 1")
panel1.watch("Dummy.val")

panel2 = manager.create_panel("Panel 2")
panel2.watch("Dummy.val")

window.show()

# Update loop
device = DummyDevice()
def update():
    registry.on_change.emit("Dummy.val", None, device.val)

timer = QTimer()
timer.timeout.connect(update)
timer.start(50)  # update every 50ms

# Save layout on close
def on_exit():
    window.save_layout(LAYOUT_FILE)

app.aboutToQuit.connect(on_exit)
sys.exit(app.exec_())
