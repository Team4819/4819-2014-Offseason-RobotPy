from framework import events, datastreams, modbase, modmaster, wpiwrap
import time
import copy
import math
try:
    import wpilib
except ImportError:
    from pyfrc import wpilib

__author__ = 'christian'

class Module(modbase.Module):

    subsystem = "controls"


    def module_load(self):
        self.stick1 = wpilib.Joystick(1)
        self.stick2 = wpilib.Joystick(2)
        self.buttons = {"trigger": False, "highShotSet": False, "medShotSet": False, "lowShotSet": False, "blowback": False, "armsUp": False, "armsDown": False, "flipper": False, "modReloader": True, "gyro_reset": False}
        self.axes = {"intake": 0, "drive-x": 0, "drive-y": 0}
        self.drivestream = datastreams.get_stream("drive")
        self.intakestream = datastreams.get_stream("intake")
        self.armsstream = datastreams.get_stream("arms")
        self.flipperstream = datastreams.get_stream("flipper")
        self.blowbackstream = datastreams.get_stream("blowback")
        self.joy1stream = datastreams.get_stream("joystick1")
        self.joy2stream = datastreams.get_stream("joystick2")
        self.gyro = wpiwrap.Gyro("Gyroscope", self.subsystem, 2, 475)

        events.set_callback("run", self.start, self.subsystem)

    def start(self):
        while not self.stop_flag:

            #Get everyting
            joy1buttons = list()
            for i in range(1,10):
                joy1buttons.append(self.stick1.GetRawButton(i))
            joy1axes = list()
            for i in range(1,4):
                joy1axes.append(self.stick1.GetRawAxis(i))
            self.joy1stream.push({"buttons": joy1buttons, "axes": joy1axes}, self.subsystem, autolock=True)
            joy2buttons = list()
            for i in range(1,10):
                joy2buttons.append(self.stick2.GetRawButton(i))
            joy2axes = list()
            for i in range(1,4):
                joy2axes.append(self.stick2.GetRawAxis(i))
            self.joy2stream.push({"buttons": joy2buttons, "axes": joy2axes}, self.subsystem, autolock=True)



            #Get button values
            last_buttons = copy.copy(self.buttons)

            self.buttons["trigger"] = self.stick1.GetRawButton(1)
            self.buttons["highShotSet"] = self.stick1.GetRawButton(2)
            self.buttons["medShotSet"] = self.stick1.GetRawButton(3)
            self.buttons["lowShotSet"] = self.stick1.GetRawButton(5)
            self.buttons["blowback"] = self.stick1.GetRawButton(8)
            self.buttons["armsUp"] = self.stick2.GetRawButton(3)
            self.buttons["armsDown"] = self.stick2.GetRawButton(2)
            self.buttons["flipper"] = self.stick2.GetRawButton(4)
            self.buttons["modReloader"] = self.stick2.GetRawButton(10)
            self.buttons["overrideBackup"] = self.stick1.GetRawButton(4)
            self.buttons["gyro_reset"] = self.stick1.GetRawButton(9)


            if self.buttons["modReloader"] and not last_buttons["modReloader"]:
                modmaster.reload_mods()

            if self.buttons["flipper"] is not last_buttons["flipper"]:
                self.flipperstream.push(self.buttons["flipper"], self.subsystem, autolock=True)

            if self.buttons["blowback"] is not last_buttons["blowback"]:
                self.blowbackstream.push(self.buttons["blowback"], self.subsystem, autolock=True)

            if self.buttons["armsDown"] and not last_buttons["armsDown"]:
                self.armsstream.push(True, self.subsystem, autolock=True)

            if self.buttons["armsUp"] and not last_buttons["armsUp"]:
                self.armsstream.push(False, self.subsystem, autolock=True)

            if self.buttons["gyro_reset"] and not last_buttons["gyro_reset"]:
                self.gyro.reset()


            #Get Axis values and threshold
            last_axis = copy.copy(self.axes)

            joy_x = self.threshold(self.stick1.GetRawAxis(1))
            joy_y = self.threshold(self.stick1.GetRawAxis(2))
            angle = self.gyro.get()
            speed_command = max(abs(joy_x), abs(joy_y))

            direction_command = math.atan2(joy_x, joy_y) * (-180/math.pi)

            angle_error = direction_command - angle

            while abs(angle_error) > 180:
                angle_error -= abs(angle_error)/angle_error * 360

            if abs(angle_error) > 100 and not self.buttons["overrideBackup"]:
                angle_error -= abs(angle_error)/angle_error * 180
                speed_command = -speed_command
            clockwise_command = angle_error/100
            if(abs(speed_command)<0.2):
                clockwise_command = 0

            self.axes["drive-x"] = clockwise_command
            self.axes["drive-y"] = speed_command

            self.axes["intake"] = self.threshold(self.stick2.GetRawAxis(2))



            #Push to data streams
            if not self.axes["drive-x"] == last_axis["drive-x"] or not self.axes["drive-y"] == last_axis["drive-y"]:
                self.drivestream.push((self.axes["drive-x"], self.axes["drive-y"]), self.subsystem, autolock=True)
            if not self.axes["intake"] == last_axis["intake"]:
                self.intakestream.push(self.axes["intake"], self.subsystem, autolock=True)


            #Shoot events:
            if self.buttons["trigger"] and not last_buttons["trigger"]:
                if self.buttons["highShotSet"]:
                    events.trigger("highShot", self.subsystem)
                elif self.buttons["medShotSet"]:
                    events.trigger("medShot", self.subsystem)
                elif self.buttons["lowShotSet"]:
                    events.trigger("lowShot", self.subsystem)

            time.sleep(.025)

    def threshold(self, number):
        if number < .01 and number > -.01:
            number = 0
        return number


