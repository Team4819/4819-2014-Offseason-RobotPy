__author__ = 'christian'
from framework import datastreams


class Module:
    subsystem = "test2"

    def __init__(self):
        self.stream = datastreams.get_stream("testStream")

    def pushStream(self):
        self.stream.push("fart", self.subsystem, autolock=True)