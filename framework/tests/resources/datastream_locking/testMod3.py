from framework.module_engine import ModuleBase

__author__ = 'christian'

from framework import datastreams


class Module(ModuleBase):
    subsystem = "test3"

    def module_load(self):
        self.stream = datastreams.get_stream("testStream")

    def lockStream(self):
        self.stream.lock(self.subsystem)

    def pushStream(self):
        self.stream.push(50, self.subsystem)