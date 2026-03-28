from functools import wraps

from debugkit.core.property import DebugProperty
from debugkit.core.registry import Registry
from debugkit.core.recorder import Recorder


def debug_property(fn=None, **kwargs):
    # If called as @debug_property (no parentheses)
    if fn is not None and callable(fn):
        return debug_property(**kwargs)(fn)

    # Otherwise return the actual decorator
    def wrapper(fn):
        dp = DebugProperty(fn, **kwargs)

        @wraps(fn)
        def wrapped(*args, **kw):
            return fn(*args, **kw)

        wrapped._debug_property = dp
        return wrapped

    return wrapper


def collect(obj, namespace=""):
    """Register all debug properties of an object to the global_registry."""
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
            global_registry.register(key, DebugProperty(**data))


global_registry: Registry = Registry()


def _test():
    def create_listener(name):
        def listener(key, old, new):
            print(f"{name}: {key} changed: {old} -> {new}")

        return listener

    listener = create_listener("A")
    listener2 = create_listener("B")
    global_registry.subscribe("Sensor1.reading", listener)

    global_registry.subscribe("Sensor2.reading", listener)
    global_registry.subscribe("Sensor2.reading", listener2)

    global_registry.emit("Sensor1.reading", 0, 1)  # triggers listener
    global_registry.emit("Sensor2.reading", "a", "b")  # does NOT trigger listener
