
from framework import modbase, events, datastreams, refrence_db
import time

try:
    import wpilib
except ImportError:
    from pyfrc import wpilib


class Module(modbase.Module):

    """This is the name used for module communication and logging.
     this should be the name of the subsystem, eg: 'drivetrain' or 'compressor' """
    name = "light_sensor"


    def module_load(self):
        self.sensor = refrence_db.get_ref("light_sensor", wpilib.AnalogChannel, 1)
        self.sensor_stream = datastreams.get_stream("light_sensor")
        events.set_callback("run", self.do_stuff, self.name)

    def do_stuff(self):
        """This is a simple run loop that says 'Hello World!' every second until the module is told to terminate."""

        #IMPORTANT! All loops that will run indefinitely MUST watch for self.stop_flag. When this is true, YOU MUST STOP!
        while not self.stop_flag:
            self.sensor_stream.push(self.sensor.GetVoltage(), self.name, autolock=True)
            time.sleep(.1)
