__author__ = 'christian'
from framework import datastreams, events


class Module:
    subsystem = "test1"

    def __init__(self):
        self.updated = False
        self.incremented = False
        self.stream = datastreams.get_stream("testStream")
        self.stream.on_update("update_testStream")
        self.stream.on_update("testStream_inc", lambda x, y: (y - x) is 1)
        events.add_callback("update_testStream", self.subsystem, self.on_stream_update)
        events.add_callback("testStream_inc", self.subsystem, self.on_stream_increment)

    def on_stream_update(self):
        self.updated = True

    def on_stream_increment(self):
        self.incremented = True

    def reset(self):
        self.updated = False
        self.incremented = False