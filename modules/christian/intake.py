from framework import events, wpiwrap, datastreams
import time
__author__ = 'christian'


class Module:

    subsystem = "intake"

    def __init__(self):
        #Get refrences
        self.joystick = wpiwrap.Joystick("Joystick 2", self.subsystem, 2)
        self.arm_solenoid = wpiwrap.Solenoid("Arm Solenoid", self.subsystem, 2)
        self.flipper_solenoid = wpiwrap.Solenoid("Flipper Solenoid", self.subsystem, 1)
        self.intake_motor = wpiwrap.Talon("Intake Motor", self.subsystem, 3)

        self.control_stream = datastreams.get_stream("intake.control")

        #Set a run loop
        events.add_callback("enabled", self.subsystem, self.run)

    def run(self, task):
        #The last state of the arms
        last_arms_state = False
        
        #disable the cannon before we do anything
        events.start_event("disable_cannon", self.subsystem)

        while task.active:

            #Read buttons
            joystick_intake_speed = self.joystick.get_axis(1)
            flipper_button = self.joystick.get_button(4)
            arms_up_button = self.joystick.get_button(3)
            arms_down_button = self.joystick.get_button(2)

            #Deadband intake speed
            if abs(joystick_intake_speed) < .1:
                joystick_intake_speed = 0

            external_control = self.control_stream.get({"controlling": False, "arms_down": False, "flipper_out": True, "intake_motor": 0})

            #Figure out who should be in charge here
            allow_external = (joystick_intake_speed is 0
                              and external_control["controlling"]
                              and not flipper_button
                              and not arms_up_button
                              and not arms_down_button)

            #If we should allow external, pass the values specified
            if allow_external:
                intake_speed = external_control["intake_motor"]
                arms_state = external_control["arms_down"]
                flipper_state = external_control["flipper_out"]

            else:
                #Otherwise, handle joystick inputs
                intake_speed = joystick_intake_speed
                flipper_state = not flipper_button
                arms_state = (last_arms_state or arms_down_button) and not arms_up_button
                #And neuteralize external inputs
                self.control_stream.push({"controlling": False, "arms_down": False, "flipper_out": True, "intake_motor": 0}, self.subsystem, autolock=True)

            #If our arm state has changed, then update the cannon disable
            if arms_state is not last_arms_state:
                if arms_state:
                    events.stop_event("disable_cannon", self.subsystem)
                else:
                    events.start_event("disable_cannon", self.subsystem)

            #And finally set our outputs
            self.intake_motor.Set(intake_speed)
            self.arm_solenoid.set(arms_state)
            self.flipper_solenoid.Set(flipper_state)

            #Update our last_arms_state variable and sleep
            last_arms_state = arms_state
            time.sleep(.05)

        self.arm_solenoid.set(False)
        self.control_stream.push({"arms_down": False, "flipper_out": True, "intake_motor": 0}, self.subsystem, autolock=True)
        events.start_event("disable_cannon", self.subsystem)