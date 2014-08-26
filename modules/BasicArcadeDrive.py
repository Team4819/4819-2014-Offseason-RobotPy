from framework import ModMaster, ModBase

__author__ = 'christian'
import time

try:
    import wpilib
except ImportError:
    from pyfrc import wpilib

class module(ModBase.module):

    name = "drivetrain"
    wants = {"controls"}

    def moduleLoad(self):
        self.leftMotor = wpilib.Talon(1)
        self.rightMotor = wpilib.Talon(2)
        ModMaster.setEventCallback("enabled", self.name, "run")
        ModMaster.setEventCallback("disabled", self.name, "stop")
        self.controlStream = ModMaster.getDataStream("drive", {0, 0}, "controls")
        super().moduleLoad()

    def stop(self):
        self.stopFlag = True

    def run(self):
        self.stopFlag = False
        print("running BasicArcadeDrive")
        while not self.stopFlag:
            InputX = float(self.controlStream.data[0])
            InputY = float(self.controlStream.data[1])
            LeftOutput = InputY + InputX
            if LeftOutput > 1 or LeftOutput < -1:
                LeftOutput = 1
            RightOutput = InputY - InputX
            if RightOutput > 1 or RightOutput < -1:
                RightOutput = 1
            self.leftMotor.Set(LeftOutput)
            self.rightMotor.Set(RightOutput)
            time.sleep(.05)
        print("BasicArcadeDrive stopped")
