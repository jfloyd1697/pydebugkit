from collections import defaultdict


class Signal:
    """
    Simple publish/subscribe signal.
    Supports multiple subscribers per signal.
    Subscribers receive all arguments passed to `emit`.
    """
    def __init__(self):
        self._subscribers = []

    def connect(self, callback):
        """Add a subscriber callback"""
        if callback not in self._subscribers:
            self._subscribers.append(callback)

    def disconnect(self, callback):
        """Remove a subscriber callback"""
        if callback in self._subscribers:
            self._subscribers.remove(callback)

    def emit(self, *args, **kwargs):
        """Notify all subscribers"""
        for callback in self._subscribers:
            callback(*args, **kwargs)


class CompositeSignal:
    """
    A signal derived from one or more source signals.
    - sources: list of DebugProperty instances or other signals with a .getter()
    - func: a function taking len(sources) arguments and returning the derived value
    - metadata: optional dict for units, color, etc.
    """
    def __init__(self, name, sources, func, metadata=None):
        self.name = name
        self.sources = sources
        self.func = func
        self.metadata = metadata or {}
        self.last_value = None
        self._subscribers = []

        # Subscribe to all source signals
        for src in self.sources:
            src.subscribe(self._on_source_update)

        # Compute initial value
        self._compute()

    def _compute(self):
        try:
            values = [src.getter() for src in self.sources]
            self.last_value = self.func(*values)
        except Exception as e:
            print(f"Error computing composite signal {self.name}: {e}")
            self.last_value = None
        return self.last_value

    def _on_source_update(self, key, value):
        val = self._compute()
        for fn in self._subscribers:
            fn(self.name, val)

    def getter(self):
        return self.last_value

    def subscribe(self, fn):
        """Subscribe a callback (key, new_value)"""
        self._subscribers.append(fn)

    def unsubscribe(self, fn):
        if fn in self._subscribers:
            self._subscribers.remove(fn)



class SignalRegistry:
    """
    Manages multiple named signals.
    Allows subscribing to signals by key.
    """
    def __init__(self):
        self._signals = defaultdict(Signal)

    def get(self, key):
        """Return the Signal object for a given key"""
        return self._signals[key]

    def connect(self, key, callback):
        """Subscribe to a named signal"""
        self._signals[key].connect(callback)

    def disconnect(self, key, callback):
        """Unsubscribe from a named signal"""
        self._signals[key].disconnect(callback)

    def emit(self, key, *args, **kwargs):
        """Emit a signal by key"""
        self._signals[key].emit(*args, **kwargs)