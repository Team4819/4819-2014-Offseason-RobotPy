from framework import ModMaster, ModBase, DataStream

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
        ModMaster.onEvent("enabled", self.run)
        ModMaster.onEvent("disabled", self.stop)
        self.controlStream = DataStream.DataStream()
        ModMaster.getMod("controls").registerDataStream("drive", self.controlStream)
        super().moduleLoad()

    def stop(self):
        self.stopFlag = True

    def run(self):
        self.stopFlag = False
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
