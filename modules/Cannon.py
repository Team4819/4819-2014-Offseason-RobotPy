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
    disableFlags = dict()

    #Controls for externally enabling and disabling cannon
    def disable(self, handleName):
        self.disableFlags[handleName] = True

    def enable(self, handleName):
        self.disableFlags[handleName] = False


    def moduleLoad(self):
        self.mainSolenoid1 = wpilib.Solenoid(1)
        self.mainSolenoid2 = wpilib.Solenoid(2)
        self.blowbackSolenoid = wpilib.Solenoid(3)

        ModMaster.getMod("controls").onEvent("highShot", self.highShot)
        ModMaster.getMod("controls").onEvent("medShot", self.medShot)
        ModMaster.getMod("controls").onEvent("lowShot", self.lowShot)
        ModMaster.getMod("controls").onEvent("blowbackOn", self.blowbackOn)
        ModMaster.getMod("controls").onEvent("blowbackOff", self.blowbackOff)

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

    def fire(self, duration=.5):

        for key in self.disableFlags:
            if self.disableFlags[key]:
                print("Not firing, cannon disabled by disableFlag " + key)
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
        print("Fired for " + str(duration) + " seconds!")
