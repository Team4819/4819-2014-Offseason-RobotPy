__author__ = 'christian'
from framework import modbase, events, wpiwrap
import time

try:
    import wpilib
except ImportError:
    from pyfrc import wpilib

class Module(modbase.Module):
    name = "encoder_test"

    def module_load(self):
        wpilib.SmartDashboard.init()
        self.encoder_1 = wpiwrap.Encoder("encoder_1", self.name, 1, 2, 360, 20)
        self.encoder_2 = wpiwrap.Encoder("encoder_2", self.name, 3, 4, 360, 20)
        events.set_callback("run", self.do_stuff, self.name)


    def do_stuff(self):
        while not self.stop_flag:
            wpilib.SmartDashboard.PutNumber("encoder_1", self.encoder_1.get())
            wpilib.SmartDashboard.PutNumber("encoder_2", self.encoder_2.get())
            time.sleep(1)
