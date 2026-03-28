from debugkit.core.signals import CompositeSignal


def collect(obj, instance=None):
    """
    Recursively collect all DebugProperties or CompositeSignals from an object/module.
    - obj: object, module, or class to inspect
    - instance: optional, the instance the properties are bound to
    Returns: dict of key -> DebugProperty or CompositeSignal
    """
    import inspect

    collected = {}

    # Iterate over all attributes
    for name, attr in inspect.getmembers(obj):
        # Skip private/internal
        if name.startswith("_"):
            continue

        # If it's a DebugProperty
        if hasattr(attr, "_debug_property"):
            dp = attr._debug_property
            dp.instance = instance or getattr(obj, "__class__", None)
            collected[name] = dp

        # If it's a CompositeSignal
        elif isinstance(attr, CompositeSignal):
            collected[name] = attr

        # Recurse into submodules or objects
        elif inspect.isclass(attr) or inspect.ismodule(attr) or inspect.isdatadescriptor(attr):
            sub_collected = collect(attr, instance=instance)
            for k, v in sub_collected.items():
                collected[f"{name}.{k}"] = v

    return collected
