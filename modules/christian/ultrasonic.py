__author__ = 'christian'
from framework import modbase, wpiwrap, datastreams, events
import time


class Module(modbase.Module):
    subsystem = "ultrasonic"

    def module_load(self):
        self.output_datastream  =  datastreams.get_stream("ultrasonic")
        self.counter = wpiwrap.Counter("Ultrasonic_Sensor", self.subsystem, 11)
        events.set_callback("run", self.run, self.subsystem)

    def run(self):
        while not self.stop_flag:
            self.output_datastream.push(self.counter.get()/0.000147, self.subsystem, autolock=True)
            time.sleep(.2)
