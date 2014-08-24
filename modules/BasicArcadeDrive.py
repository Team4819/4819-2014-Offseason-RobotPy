__author__ = 'christian'
from modules import ModBase
import time
import ModMaster
try:
    import wpilib
except ImportError:
    from pyfrc import wpilib

class module(ModBase.module):

    name = "drivetrain"

    def moduleLoad(self):
        self.leftMotor = wpilib.Talon(1)
        self.rightMotor = wpilib.Talon(2)
        ModMaster.onEvent("enabled", self.run)
        ModMaster.onEvent("disabled", self.stop)
        super().moduleLoad()

    def stop(self):
        self.stopFlag = True

    def run(self):
        self.stopFlag = False
        while not self.stopFlag:
            InputX = ModMaster.getMod("controls").DriveX
            InputY = ModMaster.getMod("controls").DriveY
            LeftOutput = InputY + InputX
            if LeftOutput > 1 or LeftOutput < -1:
                LeftOutput = 1
            RightOutput = InputY - InputX
            if RightOutput > 1 or RightOutput < -1:
                RightOutput = 1
            self.leftMotor.Set(LeftOutput)
            self.rightMotor.Set(RightOutput)
            time.sleep(.02)
        print("BasicArcadeDrive stopped")
