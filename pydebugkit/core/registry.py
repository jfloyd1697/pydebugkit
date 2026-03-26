from collections import defaultdict

class Registry:
    """Stores debug properties and allows per-key subscriptions."""
    def __init__(self):
        self._settings = {}  # key -> DebugProperty
        self._subscribers = defaultdict(list)  # key -> list of callbacks
        self._derived_dependencies = defaultdict(list)  # key -> list of deps for derived

    def register(self, key, debug_prop):
        """Register a debug property under a key."""
        self._settings[key] = debug_prop
        self.emit("__registry_updated__", key)

    def keys(self):
        """Return all registered keys."""
        return list(self._settings.keys())

    def get(self, key):
        """Return the current value of a key."""
        if key not in self._settings:
            raise KeyError(f"Key '{key}' not registered in registry")
        return self._settings[key].getter()

    def subscribe(self, key, callback):
        """Subscribe a function to a specific key."""
        self._subscribers[key].append(callback)
        return callback  # return callback for easy unsubscription

    def unsubscribe(self, key, callback):
        """Unsubscribe a function from a specific key."""
        if callback in self._subscribers[key]:
            self._subscribers[key].remove(callback)

    def emit(self, key, new_value):
        """Notify all subscribers of this key."""
        for fn in self._subscribers.get(key, []):
            fn(key, new_value)

    def register_callback(self, /, callback=None, *, key=None, **kwargs):
        """Register a callback as a DebugProperty that can be subscribed to."""
        from .property import DebugProperty

        if callback is None:
            # used as a decorator
            def callback(fn):
                return self.register_callback(fn, key=key, **kwargs)
            return callback

        def update(*args, **kwargs):
            new_val = callback(*args, **kwargs)
            self.emit(key, new_val)
            return new_val

        key = key or callback.__name__
        self.register(key, DebugProperty(update, **kwargs))
        return update

    def create_derived(self, key, func, dependencies, **kwargs):
        """
        Create a derived property.

        :param key: Name of the derived key
        :param func: Callable that takes values of dependencies and returns the derived value
        :param dependencies: List of dependency keys
        """
        # store dependencies
        self._derived_dependencies[key] = dependencies

        # define a getter that calculates the derived value dynamically
        def derived_getter():
            values = [self.get(dep) for dep in dependencies]
            return func(*values)

        # register as a normal DebugProperty
        from .property import DebugProperty
        self.register(key, DebugProperty(derived_getter, **kwargs))

        # subscribe to all dependencies so we automatically emit the derived value when they change
        def update_derived(dep_key, new):
            old_val = None
            new_val = self.get(key)
            self.emit(key, new_val)

        for dep in dependencies:
            self.subscribe(dep, update_derived)


registry = Registry()


def test():
    def create_listener(name):
        def listener(key, old, new):
            print(f"{name}: {key} changed: {old} -> {new}")
        return listener

    listener = create_listener("A")
    listener2 = create_listener("B")
    registry.subscribe("Sensor1.reading", listener)

    registry.subscribe("Sensor2.reading", listener)
    registry.subscribe("Sensor2.reading", listener2)

    registry.emit("Sensor1.reading", 0, 1)  # triggers listener
    registry.emit("Sensor2.reading", "a", "b")  # does NOT trigger listener


if __name__ == '__main__':
    test()