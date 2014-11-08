__author__ = 'christian'

from framework import events


class Module:
    subsystem = "test1"
    index = 1

    def set_callback(self):
        events.add_callback("test", self.subsystem, self.callback)

    def callback(self, task):
        self.index += 1