from framework import events, wpiwrap
import time
__author__ = 'christian'


class Module:

    subsystem = "intake"
    stop_flag = False

    def __init__(self):
        #Get refrences
        self.joystick = wpiwrap.Joystick("Joystick 2", self.subsystem, 2)
        self.arm_solenoid = wpiwrap.Solenoid("Arm Solenoid", self.subsystem, 2)
        self.flipper_solenoid = wpiwrap.Solenoid("Flipper Solenoid", self.subsystem, 1)
        self.intake_motor = wpiwrap.Talon("Intake Motor", self.subsystem, 3)

        #Set a run loop
        events.add_callback("teleoperated", self.subsystem, callback=self.run, inverse_callback=self.stop)

    def run(self):
        self.stop_flag = False
        #The last state of the arms up and arms down buttons
        arms_up_last = False
        arms_down_last = False
        
        #Set the arms to up before we do anything
        self.arm_solenoid.set(False)
        events.start_event("disable_cannon", self.subsystem)

        while not self.stop_flag:

            #Read buttons
            intake_speed = self.joystick.get_axis(1)
            flipper_button = self.joystick.get_button(4)
            arms_up = self.joystick.get_button(3)
            arms_down = self.joystick.get_button(2)

            #Deadband intake speed
            if abs(intake_speed) < .1:
                intake_speed = 0

            if arms_up and not arms_up_last:
                events.start_event("disable_cannon", self.subsystem)
                self.arm_solenoid.set(False)
            elif arms_down and not arms_down_last:
                events.stop_event("disable_cannon", self.subsystem)
                self.arm_solenoid.set(True)

            arms_down_last = arms_down
            arms_up_last = arms_up

            self.intake_motor.Set(intake_speed)
            self.flipper_solenoid.Set(not flipper_button)
            time.sleep(.05)

    def stop(self):
        self.stop_flag = True
        self.arm_solenoid.set(False)
        events.start_event("disable_cannon", self.subsystem)
