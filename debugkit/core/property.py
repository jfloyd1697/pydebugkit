from functools import wraps
from .registry import registry

class DebugProperty:
    def __init__(self, fget, trace=False, instance=None, kwargs=None):
        self.fget = fget
        self.trace = trace
        self.instance = instance  # store the bound instance
        self.kwargs = kwargs or {}

    def getter(self):
        if self.instance is None:
            return self.fget()  # call unbound if no instance
        return self.fget(self.instance)


def debug_property(trace=False, **kwargs):
    def wrapper(fn):
        dp = DebugProperty(fn, trace=trace, kwargs=kwargs)
        @wraps(fn)
        def wrapped(*args, **kwargs):
            return fn(*args, **kwargs)
        wrapped._debug_property = dp
        return wrapped
    return wrapper

def collect(obj, namespace=""):
    """Register all debug properties of an object to the registry."""
    for attr_name in dir(obj):
        attr = getattr(obj, attr_name)
        dp: DebugProperty = getattr(attr, "_debug_property", None)
        if dp is not None:
            if dp.kwargs.get("key"):
                # If a custom key is provided, use it with namespace substitution
                namespace = dp.kwargs["key"].format(**obj.__dict__)
            key = f"{namespace}.{attr_name}" if namespace else attr_name
            # create a new DebugProperty with the instance bound
            registry.register(key, DebugProperty(dp.fget, trace=dp.trace, instance=obj))