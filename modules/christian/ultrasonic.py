from framework.module_engine import ModuleBase

__author__ = 'christian'
from framework import wpiwrap, datastreams, events
import time


class Module(ModuleBase):
    subsystem = "ultrasonic"

    def __init__(self):
        self.output_datastream = datastreams.get_stream("ultrasonic")
        self.counter = wpiwrap.Counter("Ultrasonic_Sensor", self.subsystem, 11)
        events.add_callback("run", self.subsystem, self.run)

    def run(self):
        while not self.stop_flag:
            self.output_datastream.push(self.counter.get()/0.000147, self.subsystem, autolock=True)
            time.sleep(.2)
