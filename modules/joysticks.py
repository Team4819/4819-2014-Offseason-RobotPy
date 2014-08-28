from framework import events, datastreams, modbase
import time
import copy
try:
    import wpilib
except ImportError:
    from pyfrc import wpilib

__author__ = 'christian'

class Module(modbase.Module):

    name = "controls"


    def module_load(self):
        self.stick1 = wpilib.Joystick(1)
        self.stick2 = wpilib.Joystick(2)
        self.buttons = {"trigger": False, "highShotSet": False, "medShotSet": False, "lowShotSet": False, "blowback": False, "armsUp": False, "armsDown": False, "flipper": False}
        self.drivestream = datastreams.get_stream("drive")
        self.intakestream = datastreams.get_stream("intake")
        self.armsstream = datastreams.get_stream("arms")
        self.flipperstream = datastreams.get_stream("flipper")
        self.blowbackstream = datastreams.get_stream("blowback")

    def start(self):
        while not self.stop_flag:

            #Get Axis values
            drive_x = self.stick1.GetRawAxis(1)
            drive_y = self.stick1.GetRawAxis(2)
            intake = self.stick2.GetRawAxis(2)

            #Threshold values
            drive_x = self.threshold(drive_x)
            drive_y = self.threshold(drive_y)
            intake = self.threshold(intake)

            #Push to data streams
            self.drivestream.push((drive_x, drive_y), self.name, autolock=True)
            self.intakestream.push(intake, self.name, autolock=True)

            #Get button values
            last_buttons = copy.copy(self.buttons)

            self.buttons["trigger"] = self.stick1.GetRawButton(1)
            self.buttons["highShotSet"] = self.stick1.GetRawButton(2)
            self.buttons["medShotSet"] = self.stick1.GetRawButton(3)
            self.buttons["lowShotSet"] = self.stick1.GetRawButton(4)

            self.buttons["blowback"] = self.stick1.GetRawButton(5)
            self.buttons["armsUp"] = self.stick2.GetRawButton(2)
            self.buttons["armsDown"] = self.stick2.GetRawButton(4)
            self.buttons["flipper"] = self.stick2.GetRawButton(3)

            if self.buttons["flipper"] is not last_buttons["flipper"]:
                self.flipperstream.push(self.buttons["flipper"], self.name, autolock=True)

            if self.buttons["blowback"] is not last_buttons["blowback"]:
                self.blowbackstream.push(self.buttons["flipper"],self.name, autolock=True)

            if self.buttons["armsDown"] is not last_buttons["armsDown"]:
                self.armsstream.push(True, "fart", autolock=True)

            if self.buttons["armsUp"] is not last_buttons["armsUp"]:
                self.armsstream.push(False, "wheeze", autolock=True)

            #Trigger Events

            #Shoot events:
            if self.buttons["trigger"] and not last_buttons["trigger"]:
                if self.buttons["highShotSet"]:
                    events.trigger("highShot", self.name)
                elif self.buttons["medShotSet"]:
                    events.trigger("medShot", self.name)
                elif self.buttons["lowShotSet"]:
                    events.trigger("lowShot", self.name)

            time.sleep(.05)

    def threshold(self, number):
        if number < .01 and number > -.01:
            number = 0
        return number

