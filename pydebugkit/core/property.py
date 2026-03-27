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
