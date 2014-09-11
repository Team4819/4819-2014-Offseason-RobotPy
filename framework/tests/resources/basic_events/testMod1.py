__author__ = 'christian'

from framework import modbase, events


class Module(modbase.Module):
    name = "test1"
    index = 1

    def set_callback(self):
        events.set_callback("test", self.name, "callback")

    def callback(self):
        self.index += 1