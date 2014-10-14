from framework.module_engine import ModuleBase

__author__ = 'christian'

class Module(ModuleBase):
    subsystem = "test2"

    def getMessage(self):
        return "Get out of here, Now!"