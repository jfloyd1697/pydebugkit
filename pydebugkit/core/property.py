from functools import wraps
from .registry import registry

class DebugProperty:
    def __init__(self, fget, trace=False, instance=None, **kwargs):
        self.fget = fget
        self.trace = trace
        self.instance = instance  # store the bound instance
        self.kwargs = kwargs

    def getter(self):
        if self.instance is None:
            return self.fget()  # call unbound if no instance
        return self.fget(self.instance)


def debug_property(**kwargs):
    def wrapper(fn):
        dp = DebugProperty(fn, **kwargs)
        @wraps(fn)
        def wrapped(*a, **kw):
            return fn(*a, **kw)
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
            data = vars(dp)
            data["instance"] = obj
            registry.register(key, DebugProperty(**data))