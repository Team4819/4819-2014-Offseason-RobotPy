__author__ = 'christian'
from framework import events


class Module:
    subsystem = "test2"

    def fireEvent(self):
        events.trigger_event("test", self.subsystem)