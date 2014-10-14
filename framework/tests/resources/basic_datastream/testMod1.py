from framework.module_engine import ModuleBase

__author__ = 'christian'

from framework import datastreams

class Module(ModuleBase):
    subsystem = "test1"

    def module_load(self):
        self.streamData = "blank"
        self.stream = datastreams.get_stream("testStream")

    def readStream(self):
        self.streamData = self.stream.get("blank")