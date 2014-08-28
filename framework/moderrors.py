__author__ = 'christian'


class ModuleLoadError(Exception):
    def __init__(self, name, message):
        super().__init__("Module Load Error: " + name + ": " + message)


class ModuleUnloadError(Exception):
    def __init__(self, name, message):
        super().__init__("Module Unload Error: " + name + ": " + message)