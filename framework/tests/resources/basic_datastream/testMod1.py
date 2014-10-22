__author__ = 'christian'

from framework import datastreams

class Module:
    subsystem = "test1"

    def __init__(self):
        self.streamData = "blank"
        self.stream = datastreams.get_stream("testStream")

    def readStream(self):
        self.streamData = self.stream.get("blank")