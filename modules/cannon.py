from framework import modbase, events
import time
__author__ = 'christian'

try:
    import wpilib
except ImportError:
    from pyfrc import wpilib


class Module(modbase.Module):

    name = "cannon"
    disableFlags = dict()
    dryfire_protection = False

    #Controls for externally enabling and disabling cannon
    def disable(self, srcmod):
        self.disableFlags[srcmod] = True

    def enable(self, srcmod):
        self.disableFlags[srcmod] = False

    def enable_dryfire_protection(self):
        self.dryfire_protection = True

    def disable_dryfire_protection(self):
        self.dryfire_protection = False

    def module_load(self):
        self.main_solenoid_1 = wpilib.Solenoid(3)
        self.main_solenoid_2 = wpilib.Solenoid(4)
        self.blowback_solenoid = wpilib.Solenoid(5)
        self.ballpresense_switch = wpilib.DigitalInput(13)
        self.ballpresense = False

        events.set_callback("highShot", self.name, "high_shot", "controls")
        events.set_callback("medShot", self.name, "med_shot", "controls")
        events.set_callback("lowShot", self.name, "low_shot", "controls")
        events.set_callback("blowbackOn", self.name, "blowback_on", "controls")
        events.set_callback("blowbackOff", self.name, "blowback_off", "controls")

    def start(self):
        while not self.stop_flag:
            self.last_ballpresense = self.ballpresense
            self.ballpresense = self.ballpresense_switch.Get()
            if not self.last_ballpresense and self.ballpresense:
                self.trigger_event("ballPresent")
            time.sleep(.1)

    def blowback_on(self):
        self.blowback_solenoid.Set(True)

    def blowback_off(self):
        self.blowback_solenoid.Set(False)

    def high_shot(self):
        self.fire(duration=.5)

    def med_shot(self):
        self.fire(duration=.2)

    def low_shot(self):
        self.fire(duration=.1)

    def fire(self, duration=.5, enable_dryfire=False):

        for key in self.disableFlags:
            if self.disableFlags[key]:
                print("Not firing, cannon disabled by disableFlag " + key)
                return

        if not self.ballpresense and self.dryfire_protection and not enable_dryfire:
            print("Dry fire protection is On, not firing due to lack of ball")
            return

        self.main_solenoid_1.Set(True)
        self.main_solenoid_2.Set(True)
        time.sleep(duration)
        self.main_solenoid_1.Set(False)
        self.main_solenoid_2.Set(False)
        time.sleep(.2)
        self.blowback_solenoid.Set(True)
        time.sleep(.2)
        self.blowback_solenoid.Set(False)
