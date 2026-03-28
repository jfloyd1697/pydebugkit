from debugkit.core.registry import Registry
from debugkit.core.property import debug_property

registry = Registry()

class DummyDevice:
    @debug_property(name="dummy.val")
    def val(self):
        return 42

device = DummyDevice()
registry.add("Dummy.val", device.val._debug_property)
print(registry.get("Dummy.val"))