from framework.module_engine import ModuleBase

__author__ = 'christian'

from framework import events


class Module(ModuleBase):
    subsystem = "test2"

    def fireEvent(self):
        events.trigger("test", self.subsystem)