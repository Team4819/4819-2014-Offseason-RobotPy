__author__ = 'christian'

from framework import modbase, datastreams


class Module(modbase.Module):
    subsystem = "test3"

    def module_load(self):
        self.stream = datastreams.get_stream("testStream")

    def lockStream(self):
        self.stream.lock(self.subsystem)

    def pushStream(self):
        self.stream.push(50, self.subsystem)