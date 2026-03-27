# demo_inspector.py
import sys, random
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtCore import QTimer

from pydebugkit.core import collect
from pydebugkit import debug_property, global_registry
from pydebugkit.core.recorder import Recorder
from pydebugkit.ui.qt.inspector_panel import InspectorPanel


# -------------------------
# Device
# -------------------------
class Sensor:
    def __init__(self, name, initial=0, noise_pp=0.1):
        self.name = name
        self._reading = 0
        self._min = initial - noise_pp
        self._max = initial + noise_pp

    @debug_property(key="{name}", units="V", min={"attr": "_min"}, max={"attr": "_max"})
    def reading(self):
        self._reading = random.uniform(self._min, self._max)
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
global_registry.create_derived(
    "Derived.total",
    lambda *vals: sum(vals),
    [f"{sensor.name}.reading" for sensor in sensors],
    auto=False,
)
recorder.add_series("Derived.total")

inspector.populate_tree(recorder.keys())

# -------------------------
# Update Loop
# -------------------------
timer = QTimer()
timer.timeout.connect(recorder.update)
timer.start(50)

sys.exit(app.exec_())