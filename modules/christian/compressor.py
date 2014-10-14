from framework import datastreams, events, wpiwrap
import time
from framework.module_engine import ModuleBase

__author__ = 'christian'


class Module(ModuleBase):
    subsystem = "compressor"

    def module_load(self):
        self.compressor = wpiwrap.Compressor("Compressor", self.subsystem, 14, 1)
        self.pressure_switch = wpiwrap.DigitalInput("Pressure Switch", self.subsystem, 6)
        self.pressure_switch_datastream = datastreams.get_stream("pressure_switch")
        self.compressor.set(True)
        events.set_callback("run", self.run, self.subsystem)

    def run(self):
        while not self.stop_flag:
            self.pressure_switch_datastream.push(self.pressure_switch.get(), self.subsystem, autolock=True)
            time.sleep(1)

    def module_unload(self):
        self.stop_flag = True
        self.compressor.set(False)

