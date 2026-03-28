from collections import defaultdict

from debugkit.core.collector import collect as recursive_collect


class Registry:
    """
    A feature-complete registry for DebugKit:
    - Supports multiple subscribers per signal
    - Supports derived signals
    - Tracks DebugProperty metadata (name, instance, kwargs)
    - Emits notifications to all subscribers on change
    """
    def __init__(self):
        self._settings = {}      # key -> DebugProperty or value-holder
        self._signals = defaultdict(list)  # key -> list of subscriber callbacks
        self._derived = {}       # key -> function computing derived value

    # -------------------------------
    # Property registration
    # -------------------------------
    def add(self, key, prop):
        """Register a DebugProperty or value"""
        if key in self._settings:
            raise ValueError(f"Key '{key}' already exists in registry")
        self._settings[key] = prop

    def get(self, key):
        """Return current value of a property"""
        if key in self._derived:
            return self._derived[key]()
        prop = self._settings[key]
        if hasattr(prop, "getter"):
            return prop.getter()
        return prop  # raw value

    def set(self, key, value):
        """Set a property and emit notifications"""
        if key in self._settings:
            prop = self._settings[key]
            if hasattr(prop, "setter"):
                prop.setter(value)
            else:
                self._settings[key] = value
        self.emit(key, value)

    # -------------------------------
    # Signals
    # -------------------------------
    def subscribe(self, key, callback):
        """Subscribe a callback to a key"""
        self._signals[key].append(callback)

    def unsubscribe(self, key, callback):
        """Unsubscribe a callback from a key"""
        if key in self._signals:
            self._signals[key] = [c for c in self._signals[key] if c != callback]

    def emit(self, key, value):
        """Notify all subscribers"""
        for callback in self._signals.get(key, []):
            callback(key, value)

    # -------------------------------
    # Derived properties
    # -------------------------------
    def add_derived(self, key, func, dependencies):
        """
        Add a derived property that depends on other keys.
        `func` is called whenever any dependency changes.
        """
        self._derived[key] = func

        def update(_k=None, _v=None):
            val = func()
            self.emit(key, val)

        # Subscribe update callback to all dependencies
        for dep in dependencies:
            self.subscribe(dep, update)

    # -------------------------------
    # Utility
    # -------------------------------
    def all_keys(self):
        """Return all registered keys (including derived)"""
        return list(set(list(self._settings.keys()) + list(self._derived.keys())))

    def collect(self, obj):
        """
        Collect all DebugProperties and CompositeSignals from an object/module
        and add them to this registry.
        """
        collected = recursive_collect(obj, instance=obj)

        for key, prop in collected.items():
            # If it’s a DebugProperty and instance not set, assign
            if hasattr(prop, "_debug_property") and prop.instance is None:
                prop.instance = obj or getattr(obj, "__class__", None)

            # Add to registry
            self.add(key, prop)

        return collected

    def items(self):
        return self._settings.copy().items()

