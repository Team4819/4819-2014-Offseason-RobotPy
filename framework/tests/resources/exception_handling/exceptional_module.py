from framework.module_engine import ModuleBase

__author__ = 'christian'

class Module(ModuleBase):
    subsystem = "exceptional"
    message = "hi"

    def setMessage(self):
        raise Exception("This is Treason!")