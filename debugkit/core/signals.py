class Signal:
    """Optional lightweight signal-slot."""
    def __init__(self):
        self._subscribers = []

    def connect(self, fn):
        self._subscribers.append(fn)

    def emit(self, *args, **kwargs):
        for fn in self._subscribers:
            fn(*args, **kwargs)