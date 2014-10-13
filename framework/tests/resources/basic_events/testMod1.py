__author__ = 'christian'

from framework import modbase, events


class Module(modbase.Module):
    subsystem = "test1"
    index = 1

    def set_callback(self):
        events.set_callback("test", self.callback, self.subsystem)

    def callback(self):
        self.index += 1