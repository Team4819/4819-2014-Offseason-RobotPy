__author__ = 'christian'

from framework import modbase, events


class Module(modbase.Module):
    name = "test1"
    index = 1

    def module_load(self):
        events.set_callback("test", self.name, "callback")

    def reset(self):
        self.index = 1

    def callback(self):
        self.index += 1