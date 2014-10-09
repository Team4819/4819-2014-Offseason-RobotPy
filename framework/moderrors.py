__author__ = 'christian'


class ModuleLoadError(Exception):
    def __init__(self, name, message):
        super().__init__(name + ": " + message)


class ModuleUnloadError(Exception):
    def __init__(self, name, message):
        super().__init__(name + ": " + message)