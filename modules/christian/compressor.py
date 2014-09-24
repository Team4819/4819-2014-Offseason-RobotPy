from framework import modbase, datastreams, events
from framework.refrence_db import get_ref
import time
try:
    import wpilib
except ImportError:
    from pyfrc import wpilib

__author__ = 'christian'


class Module(modbase.Module):
    name = "compressor"

    def module_load(self):
        self.compressor = get_ref("compressor", wpilib.Compressor, 14, 1)
        self.pressure_switch = get_ref("pressure_switch", wpilib.DigitalInput, 6)
        self.pressure_switch_datastream = datastreams.get_stream("pressure_switch")
        self.compressor.Start()
        events.set_callback("run", self.run, self.name)

    def run(self):
        while not self.stop_flag:
            self.pressure_switch_datastream.push(self.pressure_switch.Get(), self.name, autolock=True)
            time.sleep(1)

