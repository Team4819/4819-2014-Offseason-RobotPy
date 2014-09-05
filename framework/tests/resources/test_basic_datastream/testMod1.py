__author__ = 'christian'

from framework import modbase, datastreams

class Module(modbase.Module):
    name = "test1"

    def module_load(self):
        self.streamData = "blank"
        self.stream = datastreams.get_stream("testStream")

    def readStream(self):
        self.streamData = self.stream.get("blank")