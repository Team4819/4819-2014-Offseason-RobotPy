from framework.module_engine import ModuleBase

__author__ = 'christian'

class Module(ModuleBase):
    subsystem = "exceptional"
    message = "hi"

    def setMessage(self):
        self.message = "Problem solved!"
