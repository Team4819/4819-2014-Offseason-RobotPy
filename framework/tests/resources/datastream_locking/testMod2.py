from framework.module_engine import ModuleBase

__author__ = 'christian'

from framework import datastreams


class Module(ModuleBase):
    subsystem = "test2"

    def module_load(self):
        self.stream = datastreams.get_stream("testStream")

    def pushStream(self):
        self.stream.push(100, self.subsystem, autolock=True)