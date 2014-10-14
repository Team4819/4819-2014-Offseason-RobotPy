from framework.module_engine import ModuleBase

__author__ = 'christian'

from framework import events


class Module(ModuleBase):
    subsystem = "test1"
    index = 1

    def module_load(self):
        events.set_callback("test", self.callback, self.subsystem)

    def reset(self):
        self.index = 1

    def callback(self):
        self.index += 1