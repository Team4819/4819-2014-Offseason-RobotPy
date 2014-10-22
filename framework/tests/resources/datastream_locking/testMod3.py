__author__ = 'christian'

from framework import datastreams


class Module:
    subsystem = "test3"

    def __init__(self):
        self.stream = datastreams.get_stream("testStream")

    def lockStream(self):
        self.stream.lock(self.subsystem)

    def pushStream(self):
        self.stream.push(50, self.subsystem)