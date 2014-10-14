from framework.module_engine import ModuleBase

__author__ = 'christian'

from framework import datastreams, events

class Module(ModuleBase):
    subsystem = "test1"

    def module_load(self):
        self.updated = False
        self.incremented = False
        self.stream = datastreams.get_stream("testStream")
        self.stream.on_update("update_testStream")
        self.stream.on_update("testStream_inc", lambda x, y: (y - x) is 1)
        events.set_callback("update_testStream", self.on_stream_update, self.subsystem)
        events.set_callback("testStream_inc", self.on_stream_increment, self.subsystem)

    def on_stream_update(self):
        self.updated = True

    def on_stream_increment(self):
        self.incremented = True

    def reset(self):
        self.updated = False
        self.incremented = False