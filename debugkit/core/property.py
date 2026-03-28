from functools import wraps


class DebugProperty:
    """
    Represents a debug property attached to an object or standalone.
    Supports:
    - metadata
    - optional instance binding
    - getter/setter functions
    - derived computation
    """


    def __init__(self, fget, **kwargs):
        self.fget = fget
        self.metadata = kwargs
        self.instance = None  # will be set during collect
        self._subscribers = []
        self.label_getter = None  # optional callable for display labels

    def getter(self):
        return self.fget() if self.instance is None else self.fget(self.instance)

    def subscribe(self, fn):
        self._subscribers.append(fn)

    def emit(self):
        val = self.getter()
        for fn in self._subscribers:
            fn(val)

    @property
    def label(self):
        if self.label_getter and self.instance:
            return self.label_getter(self.instance)
        return getattr(self.instance, "name", None) or self.fget.__name__


def debug_property(fn=None, *, label=None, **kwargs):
    """
    Decorator for creating DebugProperties.
    Works as:
        @debug_property
        def reading(self): ...

        @debug_property()
        def reading(self): ...

        @debug_property(label=attrgetter("name"), units="V")
        def reading(self): ...
    """
    def wrapper(f):
        dp = DebugProperty(f, **kwargs)
        dp.label_getter = label
        @wraps(f)
        def wrapped(*args, **kw):
            return f(*args, **kw)
        wrapped._debug_property = dp
        return wrapped

    # If called as @debug_property without parentheses
    if callable(fn):
        return wrapper(fn)
    # If called with parentheses or kwargs
    return wrapper