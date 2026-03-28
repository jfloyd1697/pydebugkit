import time
from collections import defaultdict
from threading import Thread, Event
from .registry import Registry


class Recorder:
    """
    Records values of registry keys at a fixed sampling interval.
    Each key is stored in a list along with timestamps.
    Subscribers can receive updated lists in real-time.
    """
    def __init__(self, registry: Registry, sample_interval=0.1):
        self.registry = registry
        self.sample_interval = sample_interval
        self._data = defaultdict(list)      # key -> list of values
        self._timestamps = []               # global timestamps
        self._subscriptions = {}            # key -> callback
        self._running = Event()
        self._thread = None

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._running.set()
        self._thread = Thread(target=self._record_loop, daemon=True)
        self._thread.start()

    # -------------------------------
    # Recording control
    # -------------------------------

    def stop(self):
        self._running.clear()
        if self._thread:
            self._thread.join()
            self._thread = None

    def pause(self):
        self._running.clear()

    def resume(self):
        if not self._thread or not self._thread.is_alive():
            self.start()
        else:
            self._running.set()

    # -------------------------------
    # Watch registration
    # -------------------------------
    def watch(self, key):
        """
        Create a watch on a registry key.
        The callback appends new values to the list and emits the updated list.
        """
        if key in self._subscriptions:
            return  # already watching

        def callback(k, value):
            timestamp = time.time()
            self._data[k].append(value)
            if k not in self._timestamps:
                self._timestamps.append(timestamp)
            # Emit the updated list to registry for live plotting
            rec_key = f"recorder.{k}"
            self.registry.emit(rec_key, list(self._data[k]))

        self.registry.subscribe(key, callback)
        self._subscriptions[key] = callback

    def unwatch(self, key):
        if key in self._subscriptions:
            self.registry.unsubscribe(key, self._subscriptions[key])
            del self._subscriptions[key]
            if key in self._data:
                del self._data[key]

    def keys(self):
        """Return the list of currently watched keys"""
        return list(self._subscriptions.keys())

    # -------------------------------
    # Recording loop (polling)
    # -------------------------------

    def _record_loop(self):
        while self._running.is_set():
            time.sleep(self.sample_interval)
            # Poll any keys that aren't automatically emitting?
            for key in self._subscriptions:
                val = self.registry.get(key)
                self._subscriptions[key](key, val)

    def is_running(self):
        return self._thread and self._thread.is_alive()

    # -------------------------------
    # Data access and utilities
    # -------------------------------

    def get_data(self, key):
        """Return the list of recorded values for a key"""
        return self._data.get(key, [])

    def get_timestamps(self):
        return self._timestamps

    def clear(self):
        """Clear all recorded data"""
        self._data.clear()
        self._timestamps.clear()