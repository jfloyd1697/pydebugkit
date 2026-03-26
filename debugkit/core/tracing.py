import time
from collections import defaultdict

class TraceStore:
    def __init__(self):
        self._data = defaultdict(list)

    def record(self, key, value):
        self._data[key].append((time.time(), value))

    def get(self, key):
        return self._data[key]

trace = TraceStore()
