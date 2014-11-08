__author__ = 'christian'

from framework import events


class Module:
    subsystem = "test1"
    index = 1

    def __init__(self):
        events.add_callback("test", self.subsystem, self.callback)

    def reset(self):
        self.index = 1

    def callback(self, task):
        self.index += 1