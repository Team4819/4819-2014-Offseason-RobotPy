
from framework import events, datastreams, wpiwrap
import time
from framework.module_engine import ModuleBase


class Module(ModuleBase):

    """This is the name used for module communication and logging.
     this should be the name of the subsystem, eg: 'drivetrain' or 'compressor' """
    subsystem = "light_sensor"


    def module_load(self):
        self.sensor = wpiwrap.AnalogInput("Light Sensor", self.subsystem, 1)
        self.sensor_stream = datastreams.get_stream("light_sensor")
        events.set_callback("run", self.do_stuff, self.subsystem)

    def do_stuff(self):
        """This is a simple run loop that says 'Hello World!' every second until the module is told to terminate."""

        #IMPORTANT! All loops that will run indefinitely MUST watch for self.stop_flag. When this is true, YOU MUST STOP!
        while not self.stop_flag:
            self.sensor_stream.push(self.sensor.GetVoltage(), self.subsystem, autolock=True)
            time.sleep(.1)
