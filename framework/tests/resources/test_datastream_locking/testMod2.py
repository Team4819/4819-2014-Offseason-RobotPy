__author__ = 'christian'

from framework import modbase, datastreams


class Module(modbase.Module):
    name = "test2"

    def module_load(self):
        self.stream = datastreams.get_stream("testStream")

    def pushStream(self):
        self.stream.push(100, self.name, autolock=True)