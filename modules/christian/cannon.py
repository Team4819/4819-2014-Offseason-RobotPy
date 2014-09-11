from framework import modbase, events, datastreams
from framework.refrence_db import get_ref
import time
import logging
__author__ = 'christian'

try:
    import wpilib
except ImportError:
    from pyfrc import wpilib


class Module(modbase.Module):

    name = "cannon"
    disableFlags = dict()
    dryfire_protection = False

    def module_load(self):

        self.main_solenoid_1 = get_ref("main_solenoid_1", wpilib.Solenoid, 3)
        self.main_solenoid_2 = get_ref("main_solenoid_2", wpilib.Solenoid, 4)
        self.blowback_solenoid = get_ref("blowback_solenoid", wpilib.Solenoid, 5)
        self.ballpresense_switch = get_ref("ballpresence_switch", wpilib.DigitalInput, 13)

        self.ballpresense = False

        self.blowback_stream = datastreams.get_stream("blowback")

        events.set_callback("highShot", self.high_shot, self.name)
        events.set_callback("medShot", self.med_shot, self.name)
        events.set_callback("lowShot", self.low_shot, self.name)
        events.set_callback("run", self.run, self.name)

    #Controls for externally enabling and disabling cannon
    def disable(self, srcmod):
        self.disableFlags[srcmod] = True

    def enable(self, srcmod):
        self.disableFlags[srcmod] = False

    def enable_dryfire_protection(self):
        self.dryfire_protection = True

    def disable_dryfire_protection(self):
        self.dryfire_protection = False

    def run(self):
        while not self.stop_flag:
            self.last_ballpresense = self.ballpresense
            self.ballpresense = self.ballpresense_switch.Get()
            if not self.last_ballpresense and self.ballpresense:
                self.trigger_event("ballPresent")
            self.blowback_solenoid.Set(self.blowback_stream.get(False))
            time.sleep(.1)

    def high_shot(self):
        self.fire(duration=.5)

    def med_shot(self):
        self.fire(duration=.2)

    def low_shot(self):
        self.fire(duration=.1)

    def fire(self, duration=.5, enable_dryfire=False):
        for key in self.disableFlags:
            if self.disableFlags[key]:
                logging.info("Not firing, cannon disabled by disableFlag " + key)
                return

        if not self.ballpresense and self.dryfire_protection and not enable_dryfire:
            logging.info("Dry fire protection is On, not firing due to lack of ball")
            return

        self.main_solenoid_1.Set(True)
        self.main_solenoid_2.Set(True)
        time.sleep(duration)
        self.main_solenoid_1.Set(False)
        self.main_solenoid_2.Set(False)
        time.sleep(.2)
        self.blowback_stream.push(True, self.name, autolock=True)
        time.sleep(.2)
        self.blowback_stream.push(False, self.name, autolock=True)
