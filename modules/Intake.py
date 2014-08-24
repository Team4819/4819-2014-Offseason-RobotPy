from framework import ModMaster, ModBase

__author__ = 'christian'
import time
import threading
try:
    import wpilib
except ImportError:
    from pyfrc import wpilib


class module(ModBase.module):

    name = "intake"

    def moduleLoad(self):
        self.armSolenoid = wpilib.Solenoid(4)
        self.flipperSolenoid = wpilib.Solenoid(5)
        self.intakeMotor = wpilib.Talon(3)

        ModMaster.getMod("controls").onEvent("armsUp", self.armsUp)
        ModMaster.getMod("controls").onEvent("armsDown", self.armsDown)
        ModMaster.getMod("controls").onEvent("flipperIn", self.flipperIn)
        ModMaster.getMod("controls").onEvent("flipperOut", self.flipperOut)
        ModMaster.onEvent("enabled", self.run)
        ModMaster.onEvent("disabled", self.disable)

    def disable(self):
        self.stopFlag = True

    def run(self):
        self.stopFlag = False
        while not self.stopFlag:
            self.intakeMotor.Set(ModMaster.getMod("controls").intake)
            time.sleep(.2)
        print("Intake Stopped")

    def armsUp(self):
        ModMaster.getMod("cannon").disable(self.name)
        self.armSolenoid.Set(True)

    def armsDown(self):
        self.armSolenoid.Set(False)
        time.sleep(.5)
        ModMaster.getMod("cannon").enable(self.name)

    def flipperIn(self):
        self.flipperSolenoid.Set(True)

    def flipperOut(self):
        self.flipperSolenoid.Set(False)

