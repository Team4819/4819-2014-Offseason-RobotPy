__author__ = 'christian'

from framework import modbase, events


class Module(modbase.Module):
    name = "test2"

    def fireEvent(self):
        events.trigger("test", self.name)