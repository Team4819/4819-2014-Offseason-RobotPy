from framework import events, wpiwrap
import time
import logging
__author__ = 'christian'


class Module:

    subsystem = "cannon"
    enabled = True
    stop_flag = False

    def __init__(self):

        #Get Device Refrences
        self.main_solenoid_1 = wpiwrap.Solenoid("Cannon Solenoid 1", self.subsystem, 3)
        self.main_solenoid_2 = wpiwrap.Solenoid("Cannon Solenoid 2", self.subsystem, 4)
        self.blowback_solenoid = wpiwrap.Solenoid("Blowback Solenoid", self.subsystem, 5)
        self.joystick = wpiwrap.Joystick("Joystick 1", self.subsystem, 1)

        #Set event callbacks

        #Shot events
        events.add_callback("shoot_cannon", self.subsystem, self.high_shot)

        #Cannon disable events
        events.add_callback("disable_cannon", self.subsystem, self.disable)
        events.add_inverse_callback("disable_cannon", self.subsystem, self.enable)

        #Run loops
        events.add_callback("teleoperated", self.subsystem, self.cannon_loop)
        events.add_callback("teleoperated", self.subsystem, self.blowback_loop)

    def disable(self, task):
        """Disables the cannon"""
        self.enabled = False

    def enable(self, task):
        """Enables the cannon"""
        self.enabled = True

    def cannon_loop(self, task):
        """Watches joystick input and fires cannon"""
        last_trigger = False
        while task.active:

            #Get joystick button values
            trigger = self.joystick.get_button(1)
            high_shot = self.joystick.get_button(2)
            med_shot = self.joystick.get_button(3)
            low_shot = self.joystick.get_button(5)

            #Trigger rising edge detector
            if trigger and not last_trigger:
                if high_shot:
                    self.fire(duration=.5)
                elif med_shot:
                    self.fire(duration=.2)
                elif low_shot:
                    self.fire(duration=.1)

            last_trigger = trigger

            time.sleep(.1)

    #The blowback can be a lot slower of reaction than the cannon, so we put it in it's own loop to conserve cpu usage
    def blowback_loop(self, task):
        """Watches joystick input and operates cannon blowback"""
        last_blowback = False
        while task.active:
            blowback = self.joystick.get_button(4)
            if blowback is not last_blowback:
                self.blowback_solenoid.set(blowback)
            last_blowback = blowback
            time.sleep(.3)

    def high_shot(self, task):
        self.fire()

    def fire(self, duration=.5):
        """Fire the cannon, with the solenoids on for the period specified."""

        if not self.enabled:
            logging.info("Not firing, cannon disabled")
            return

        #Fire cannon
        self.main_solenoid_1.set(True)
        self.main_solenoid_2.set(True)
        time.sleep(duration)
        self.main_solenoid_1.set(False)
        self.main_solenoid_2.set(False)

        #Wait a bit
        time.sleep(.2)

        #Attempt to retract cannon
        self.blowback_solenoid.set(True)
        time.sleep(.2)
        self.blowback_solenoid.set(False)
