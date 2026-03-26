# demo_inspector.py
import sys, random
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtCore import QTimer

from debugkit.core.registry import registry
from debugkit.core.property import debug_property, collect
from debugkit.core.recorder import Recorder
from debugkit.ui.qt.inspector_panel import InspectorPanel


# -------------------------
# Device
# -------------------------
class Sensor:
    def __init__(self, name):
        self.name = name
        self._reading = 0

    @debug_property(key="{name}", trace=True)
    def reading(self):
        self._reading += random.random() - 0.5
        return self._reading


# -------------------------
# Setup App
# -------------------------
app = QApplication(sys.argv)

window = QMainWindow()
window.setWindowTitle("DebugKit Inspector Demo")

central = QWidget()
layout = QVBoxLayout(central)
window.setCentralWidget(central)

# Inspector
inspector = InspectorPanel()
layout.addWidget(inspector)

window.resize(1000, 600)
window.show()

# -------------------------
# Create Sensors
# -------------------------
sensors = [Sensor(f"Sensor{i+1}") for i in range(3)]

for sensor in sensors:
    collect(sensor)

# -------------------------
# Recorder (event-driven)
# -------------------------
recorder = Recorder([f"{sensor.name}.reading" for sensor in sensors])

# -------------------------
# Derived Signal
# -------------------------
registry.create_derived(
    "Derived.total",
    lambda *vals: sum(vals),
    [f"{sensor.name}.reading" for sensor in sensors]
)
recorder.add_series("Derived.total")

# -------------------------
# Update Loop
# -------------------------
def update():
    for sensor in sensors:
        val = registry.get(f"{sensor.name}.reading")
        registry.emit(f"{sensor.name}.reading", val)

timer = QTimer()
timer.timeout.connect(update)
timer.start(50)

sys.exit(app.exec_())