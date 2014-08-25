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
        self.buttons = {"trigger": False, "highShotSet": False, "medShotSet": False, "lowShotSet": False, "blowbackOn": False, "blowbackOff": False, "armsUp": False, "armsDown": False, "flipperIn": False, "flipperOut": False}

        while not self.stopFlag:

            #Set Drive values
            self.DriveX = self.stick1.GetRawAxis(1)
            self.DriveY = self.stick1.GetRawAxis(2)

            #Threshold drive values
            if self.DriveX < .01 and self.DriveX > -.01:
                self.DriveX = 0

            if self.DriveY < .01 and self.DriveY > -.01:
                self.DriveY = 0

            self.setDataStream("drive", (self.DriveX, self.DriveY))

            #Get Intake Motor Value
            self.setDataStream("intake", self.stick2.GetRawAxis(2))


            #Set button values
            lastButtons = copy.copy(self.buttons)
            self.buttons["trigger"] = self.stick1.GetRawButton(1)
            self.buttons["highShotSet"] = self.stick1.GetRawButton(2)
            self.buttons["medShotSet"] = self.stick1.GetRawButton(3)
            self.buttons["lowShotSet"] = self.stick1.GetRawButton(4)
            self.buttons["blowbackOn"] = self.stick1.GetRawButton(5)
            self.buttons["blowbackOff"] = not self.buttons["blowbackOn"]
            self.buttons["armsUp"] = self.stick2.GetRawButton(2)
            self.buttons["armsDown"] = self.stick2.GetRawButton(4)
            self.buttons["flipperIn"] = self.stick2.GetRawButton(3)
            self.buttons["flipperOut"] = not self.buttons["flipperIn"]


            #Trigger Events

            #Shoot events:
            if self.buttons["trigger"] and not lastButtons["trigger"]:
                if self.buttons["highShotSet"]:
                    self.setEvent("highShot")
                elif self.buttons["medShotSet"]:
                    self.setEvent("medShot")
                elif self.buttons["lowShotSet"]:
                    self.setEvent("lowShot")

            #Fire event for rising edge of any button
            for key in self.buttons:
                if self.buttons[key] and not lastButtons[key]:
                    self.setEvent(key)


            time.sleep(.05)
        print("2Joysticks Stopped")


