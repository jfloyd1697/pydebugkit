import sys, random, os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
from debugkit.ui.qt.main_window import DebugMainWindow
from debugkit.ui.qt.plot_manager import MultiPanelPlotManager
from debugkit import debug_property, global_registry
import pyqtgraph as pg


# --- Device class ---
class Sensor:
    def __init__(self):
        self._reading = 0

    @debug_property
    def reading(self):
        self._reading += random.random() - 0.5
        return self._reading


# --- Setup application ---
app = QApplication(sys.argv)
window = DebugMainWindow(global_registry)
manager = MultiPanelPlotManager(window)

# --- Create multiple sensor instances ---
sensors, namespaces, colors = zip(*[(Sensor(), f"Sensor{i+1}", pg.intColor(i))  for i in range(8)])

for sensor, ns in zip(sensors, namespaces):
    global_registry.collect(sensor)

# --- Panel 1: overlay raw sensors ---
raw_panel = manager.create_panel("Raw Sensors Overlay")
for ns, color in zip(namespaces, colors):
    raw_panel.add_series(f"{ns}.reading", pen=color)
raw_panel.add_series("update", pen="m", width=2)

# --- Panel 2: derived signals ---
derived_panel = manager.create_panel("Derived Signals")
derived_panel.add_series("Derived.total", pen="w", width=2)
derived_panel.add_series("Derived.max", pen="w", width=2)
derived_panel.add_series("Derived.min", pen="w", width=2)
derived_panel.add_series("Derived.update", pen="m", width=2)

# global_registry.create_derived("Derived.total", lambda *v: sum(v), [f"{ns}.reading" for ns in namespaces])
# global_registry.create_derived("Derived.max", lambda *v: max(v), [f"{ns}.reading" for ns in namespaces])
# global_registry.create_derived("Derived.min", lambda *v: min(v), [f"{ns}.reading" for ns in namespaces])
# global_registry.create_derived("Derived.update", lambda *v: int(int(100 * v[0]) % 2), ["Derived.total"])

window.show()


# --- Update loop ---
# @global_registry.register_callback()
def update():
    vals = []
    for ns in global_registry.all_keys():
        val = global_registry.get(ns)
        global_registry.emit(ns, val)
        vals.append(val)
    return int(int(100 * sum(vals)) % 2)


timer = QTimer()
timer.timeout.connect(update)
timer.start(50)  # 50ms update

sys.exit(app.exec_())
