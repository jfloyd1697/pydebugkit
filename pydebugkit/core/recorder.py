# recorder.py
import time
from collections import defaultdict
from pydebugkit.core import global_registry
from pydebugkit.core.property import DebugProperty


class Recorder:
    def __init__(self, keys, namespace="Recorder", max_len=1000):
        self.namespace = namespace
        self.max_len = max_len

        self._data = defaultdict(list)
        self._timestamps = defaultdict(list)

        self._setup(keys)

    def update(self):
        for key in self.keys():
            global_registry.update(key)

    # -------------------------
    # Setup
    # -------------------------
    def _setup(self, keys):
        for key in keys:
            self.add_series(key)

    def add_series(self, key):
        rec_key = self._make_rec_key(key)
        self._data[rec_key] = []

        # -------------------------
        # History property
        # -------------------------
        global_registry.register(
            rec_key,
            DebugProperty(lambda k=key: list(self._data[k]), tags=["recorder_history"])
        )

        # -------------------------
        # Latest value property
        # -------------------------
        latest_key = f"{rec_key}_latest"
        global_registry.register(
            latest_key,
            DebugProperty(lambda k=key: self._data[k][-1] if self._data[k] else None, tags=["recorder_latest"])
        )

        # -------------------------
        # Timestamp property
        # -------------------------
        ts_key = f"{rec_key}_timestamps"
        global_registry.register(
            ts_key,
            DebugProperty(lambda k=key: list(self._timestamps[k]), tags=["recorder_timestamps"])
        )

        # -------------------------
        # Subscribe to source signal
        # -------------------------
        global_registry.subscribe(key, self._make_callback(key, rec_key, latest_key, ts_key))

    def _make_rec_key(self, key):
        return f"{self.namespace}.{key}"

    # -------------------------
    # Callback
    # -------------------------
    def _make_callback(self, source_key, rec_key, latest_key, ts_key):
        def callback(key, new):
            now = time.time()

            # append value + timestamp
            self._data[source_key].append(new)
            self._timestamps[source_key].append(now)

            # enforce max length (rolling buffer)
            if self.max_len:
                if len(self._data[source_key]) > self.max_len:
                    self._data[source_key].pop(0)
                    self._timestamps[source_key].pop(0)

            # emit updates (COPY to avoid mutation bugs)
            global_registry.emit(rec_key, list(self._data[source_key]))
            global_registry.emit(latest_key, new)
            global_registry.emit(ts_key, list(self._timestamps[source_key]))

        return callback

    # -------------------------
    # Helpers
    # -------------------------
    def get_series(self, key):
        return self._data[key]

    def get_timestamps(self, key):
        return self._timestamps[key]

    def keys(self):
        return list(self._data.keys())
