from framework import modbase, datastreams, events, wpiwrap
import time

__author__ = 'christian'


class Module(modbase.Module):
    name = "compressor"

    def module_load(self):
        self.compressor = wpiwrap.Compressor("Compressor", self.name, 14, 1)
        self.pressure_switch = wpiwrap.DigitalInput("Pressure Switch", self.name, 6)
        self.pressure_switch_datastream = datastreams.get_stream("pressure_switch")
        self.compressor.set(True)
        events.set_callback("run", self.run, self.name)

    def run(self):
        while not self.stop_flag:
            self.pressure_switch_datastream.push(self.pressure_switch.get(), self.name, autolock=True)
            time.sleep(1)

    def module_unload(self):
        self.stop_flag = True
        self.compressor.set(False)

