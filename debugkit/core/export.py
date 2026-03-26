import csv
import json
from .tracing import trace

def export_csv(path):
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["key", "timestamp", "value"])
        for key, data in trace._data.items():
            for ts, value in data:
                writer.writerow([key, ts, value])

def export_json(path):
    with open(path, "w") as f:
        json.dump(trace._data, f, indent=2)

def load_json(path):
    global trace
    with open(path) as f:
        trace._data = json.load(f)
