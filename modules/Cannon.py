__author__ = 'christian'
from modules import ModBase
import time
import ModMaster
try:
    import wpilib
except ImportError:
    from pyfrc import wpilib

class module(ModBase.module):

    name = "cannon"

    disabledTimer = 0

    def disableFor(self, time):
        if time > self.disabledTimer:
            self.disabledTimer = time

    def moduleLoad(self):
        self.mainSolenoid1 = wpilib.Solenoid(1)
        self.mainSolenoid2 = wpilib.Solenoid(2)
        self.blowbackSolenoid = wpilib.Solenoid(3)

        ModMaster.getMod("controls").onEvent("shoot", self.fire)

        while not self.stopFlag:
            if self.disabledTimer > 0:
                self.disabledTimer -= .5
            time.sleep(.5)

    def fire(self, duration=.5):
        if self.disabledTimer > 0:
            print("Not firing, Cannon disabled!")
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
        print("Fired!")
