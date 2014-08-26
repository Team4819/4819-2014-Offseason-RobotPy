from framework import ModMaster, ModBase

__author__ = 'christian'
import time
import threading
try:
    import wpilib
except ImportError:
    from pyfrc import wpilib


class module(ModBase.module):

    name = "cannon"
    wants = {"Compressor", "controls"}
    disableFlags = dict()
    dryFireProtection = False

    #Controls for externally enabling and disabling cannon
    def disable(self, handleName):
        self.disableFlags[handleName] = True

    def enable(self, handleName):
        self.disableFlags[handleName] = False

    def enableDryFireProtection(self):
        self.dryFireProtection = True

    def disableDryFireProtection(self):
        self.dryFireProtection = False

    def moduleLoad(self):
        self.mainSolenoid1 = wpilib.Solenoid(3)
        self.mainSolenoid2 = wpilib.Solenoid(4)
        self.blowbackSolenoid = wpilib.Solenoid(5)
        self.ballPresenseSwitch = wpilib.DigitalInput(13)
        self.ballPresense = False

        ModMaster.setEventCallback("highShot", self.name, "highShot", "controls")
        ModMaster.setEventCallback("medShot", self.name, "medShot", "controls")
        ModMaster.setEventCallback("lowShot", self.name, "lowShot", "controls")
        ModMaster.setEventCallback("blowbackOn", self.name, "blowbackOn", "controls")
        ModMaster.setEventCallback("blowbackOff", self.name, "blowbackOff", "controls")

        while not self.stopFlag:
            self.lastBallPresense = self.ballPresense
            self.ballPresense = self.ballPresenseSwitch.Get()
            if not self.lastBallPresense and self.ballPresense:
                self.triggerEvent("ballPresent")
            time.sleep(.1)

    def blowbackOn(self):
        self.blowbackSolenoid.Set(True)

    def blowbackOff(self):
        self.blowbackSolenoid.Set(False)

    def highShot(self):
        self.fire(duration=.5)

    def medShot(self):
        self.fire(duration=.2)

    def lowShot(self):
        self.fire(duration=.1)

    def fire(self, duration=.5, enableDryFire = False):

        for key in self.disableFlags:
            if self.disableFlags[key]:
                print("Not firing, cannon disabled by disableFlag " + key)
                return

        if not self.ballPresense and self.dryFireProtection and not enableDryFire:
            print("Dry fire protection is On, not firing due to lack of ball")
            return

        self.mainSolenoid1.Set(True)
        self.mainSolenoid2.Set(True)
        time.sleep(duration)
        self.mainSolenoid1.Set(False)
        self.mainSolenoid2.Set(False)
        time.sleep(.2)
        self.blowbackSolenoid.Set(True)
        time.sleep(.2)
        self.blowbackSolenoid.Set(False)
