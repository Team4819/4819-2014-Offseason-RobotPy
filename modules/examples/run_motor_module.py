"""This is an example module demonstrating the use of actual robot hardware.
 While the robot is enabled it will spin a motor on pwm 1"""
from framework import events, wpiwrap


class Module:
    """Just a happy motor-spinning module!"""

    subsystem = "motor spinner"

    def __init__(self):

        #This creates a refrence to a Talon motor controller, which is controlled over pwm from the Digital Sidecar.
        #
        #wpiwrap is a custom wrapper for wpilib, it primarily allows for multiple refrences to the same hardware, which
        #standard wpilib does not allow. It also incorporates with module_engine to neuteralize outputs when modules are
        #unloaded.
        #
        #Here we are passing three arguments to the new Talon object: it's name, here "Spinny_thing", our subsystem name,
        #and the pwm port on the Digital sidecar to use.

        self.spinner_thing = wpiwrap.Talon("Spinny_thing", self.subsystem, 1)

        #The only difference here from the last example is that we are running the event upon the robot being enabled,
        #and stopping it when the robot gets disabled
        events.add_callback("teleoperated", self.subsystem, callback=self.spin_the_spinny_thing, inverse_callback=self.stop_the_spinny_thing)

    def spin_the_spinny_thing(self):
        """This sets the motor to run at half speed"""
        #The way this stuff works, when you set the value of a motor, it will run at that speed until either it is told
        # to do something else, or the robot is disabled, which automatically shuts down all outputs.
        self.spinner_thing.set(.5)

    def stop_the_spinny_thing(self):
        """This stops the motor"""
        self.spinner_thing.set(0)
