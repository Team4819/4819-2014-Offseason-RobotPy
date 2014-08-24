__author__ = 'christian'
from modules import controls
import time
import copy
try:
    import wpilib
except ImportError:
    from pyfrc import wpilib

class module(controls.module):

    name = "controls"


    def moduleLoad(self):
        self.stick1 = wpilib.Joystick(1)
        self.stick2 = wpilib.Joystick(2)
        self.buttons = dict()
        self.buttons["trigger"] = False

        while not self.stopFlag:

            #Set Drive values
            self.DriveX = self.stick1.GetRawAxis(1)
            if self.DriveX < .01 and self.DriveX > -.01:
                self.DriveX = 0
            self.DriveY = self.stick1.GetRawAxis(2)
            if self.DriveY < .01 and self.DriveY > -.01:
                self.DriveY = 0

            #Set button values
            lastButtons = copy.copy(self.buttons)
            self.buttons["trigger"] = self.stick1.GetRawButton(1)

            if self.buttons["trigger"] and not lastButtons["trigger"]:
                self.setEvent("shoot")

            time.sleep(.02)
        print("2Joysticks Stopped")


