__author__ = 'christian'

from framework import modbase, events, datastreams
try:
    import wpilib
except ImportError:
    from pyfrc import wpilib
import time
import json

class Module(modbase.Module):

    name = "dashboard"

    def module_load(self):
        wpilib.SmartDashboard.init()
        self.pressure_switch = datastreams.get_stream("pressure_switch")
        self.joystick1 = datastreams.get_stream("joystick1")
        self.joystick2 = datastreams.get_stream("joystick2")
        events.set_callback("run", self.run, self.name)


    def run(self):
        while not self.stop_flag:
            wpilib.SmartDashboard.PutBoolean("pressure switch", self.pressure_switch.get(False))
            default = {"buttons": (False, False, False, False, False, False, False, False, False, False), "axes": (0,0,0,0)}
            joy1string = json.dumps(self.joystick1.get(default))
            joy2string = json.dumps(self.joystick2.get(default))
            wpilib.SmartDashboard.PutString("joystick1", joy1string)
            wpilib.SmartDashboard.PutString("joystick2", joy2string)
            time.sleep(.5)

