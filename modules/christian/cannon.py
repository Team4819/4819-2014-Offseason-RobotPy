from framework import events, datastreams, wpiwrap
import time
import logging
from framework.module_engine import ModuleBase

__author__ = 'christian'


class Module(ModuleBase):

    subsystem = "cannon"
    disableFlags = dict()
    dryfire_protection = False

    def module_load(self):
        self.main_solenoid_1 = wpiwrap.Solenoid("Cannon Solenoid 1", self.subsystem, 3)
        self.main_solenoid_2 = wpiwrap.Solenoid("Cannon Solenoid 2", self.subsystem, 4)
        self.blowback_solenoid = wpiwrap.Solenoid("Blowback Solenoid", self.subsystem, 5)
        self.ballpresense_switch = wpiwrap.DigitalInput("Ball Presence Switch", self.subsystem, 13)

        self.ballpresense = False

        self.ballpresense_stream = datastreams.get_stream("ballpresence")
        self.ballpresense_stream.on_update("ballPresent", lambda x, y: not x and y)

        self.blowback_stream = datastreams.get_stream("blowback")

        events.set_callback("highShot", self.high_shot, self.subsystem)
        events.set_callback("medShot", self.med_shot, self.subsystem)
        events.set_callback("lowShot", self.low_shot, self.subsystem)
        events.set_callback("run", self.run, self.subsystem)

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
            self.ballpresense = self.ballpresense_switch.Get()
            self.ballpresense_stream.push(self.ballpresense, self.subsystem, True)
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
        self.blowback_stream.push(True, self.subsystem, autolock=True)
        time.sleep(.2)
        self.blowback_stream.push(False, self.subsystem, autolock=True)
