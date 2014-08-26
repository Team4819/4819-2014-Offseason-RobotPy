from framework import ModMaster, ModBase
from framework.ModMaster import DataStream

__author__ = 'christian'
import time

import threading
try:
    import wpilib
except ImportError:
    from pyfrc import wpilib


class module(ModBase.module):

    name = "intake"
    wants = {"compressor", "controls"}

    def moduleLoad(self):
        self.armSolenoid = wpilib.Solenoid(2)
        self.flipperSolenoid = wpilib.Solenoid(1)
        self.intakeMotor = wpilib.Talon(3)

        ModMaster.setEventCallback("armsUp", self.name, "armsUp", srcmod="controls")
        ModMaster.setEventCallback("armsDown", self.name, "armsDown", srcmod="controls")
        ModMaster.setEventCallback("flipperIn", self.name, "flipperIn", srcmod="controls")
        ModMaster.setEventCallback("flipperOut", self.name, "flipperOut", srcmod="controls")
        ModMaster.setEventCallback("enabled", self.name, "run")
        ModMaster.setEventCallback("enabled", self.name, "flipperOut")
        ModMaster.setEventCallback("disabled", self.name, "disable")
        ModMaster.setEventCallback("disabled", self.name, "flipperIn")

        #Setup data stream for wheels
        self.intakeDrive = ModMaster.getDataStream("intake", 0, srcmod="controls")

    def disable(self):
        self.stopFlag = True
        self.armsUp()

    def run(self):
        self.stopFlag = False
        self.armsUp()
        while not self.stopFlag:
            self.intakeMotor.Set(float(self.intakeDrive.data))
            time.sleep(.05)
        print("Intake Stopped")

    def armsUp(self):
        ModMaster.getMod("cannon").disable(self.name)
        self.armSolenoid.Set(True)

    def armsDown(self):
        self.armSolenoid.Set(False)
        time.sleep(.5)
        ModMaster.getMod("cannon").enable(self.name)

    def flipperIn(self):
        self.flipperSolenoid.Set(False)

    def flipperOut(self):
        self.flipperSolenoid.Set(True)

