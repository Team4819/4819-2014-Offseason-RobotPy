__author__ = 'christian'

from framework import modbase, datastreams


class Module(modbase.Module):
    subsystem = "test2"

    def module_load(self):
        self.stream = datastreams.get_stream("testStream")

    def pushStream(self):
        self.stream.push("fart", self.subsystem, autolock=True)