__author__ = 'christian'

from framework import modbase, events, datastreams, wpiwrap
try:
    import wpilib
except ImportError:
    from pyfrc import wpilib
import time
import json
import logging

class Module(modbase.Module):

    name = "dashboard"

    def module_load(self):
        wpilib.SmartDashboard.init()
        self.pressure_switch = datastreams.get_stream("pressure_switch")
        self.joystick1 = datastreams.get_stream("joystick1")
        self.joystick2 = datastreams.get_stream("joystick2")
        self.ball_presence = datastreams.get_stream("ballpresence")
        self.light_sensor = datastreams.get_stream("light_sensor")
        events.set_callback("run", self.run, self.name)


    def run(self):
        while not self.stop_flag:
            try:
                wpiwrap.publish_values()
            except Exception as e:
                logging.error(e)
            default = {"buttons": (False, False, False, False, False, False, False, False, False, False), "axes": (0,0,0,0)}
            joy1string = json.dumps(self.joystick1.get(default))
            joy2string = json.dumps(self.joystick2.get(default))
            wpilib.SmartDashboard.PutString("joystick1", joy1string)
            wpilib.SmartDashboard.PutString("joystick2", joy2string)
            time.sleep(.5)

