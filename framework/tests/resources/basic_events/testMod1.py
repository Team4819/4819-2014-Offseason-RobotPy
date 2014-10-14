from framework.module_engine import ModuleBase

__author__ = 'christian'

from framework import events


class Module(ModuleBase):
    subsystem = "test1"
    index = 1

    def set_callback(self):
        events.set_callback("test", self.callback, self.subsystem)

    def callback(self):
        self.index += 1