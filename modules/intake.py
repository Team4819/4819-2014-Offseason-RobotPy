from framework import modmaster, modbase, datastreams, events
import time
__author__ = 'christian'


try:
    import wpilib
except ImportError:
    from pyfrc import wpilib


class Module(modbase.Module):

    name = "intake"


    def module_load(self):
        self.arm_solenoid = wpilib.Solenoid(2)
        self.flipper_solenoid = wpilib.Solenoid(1)
        self.intake_motor = wpilib.Talon(3)

        self.armstream = datastreams.get_stream("arms")
        self.armstream.on_update("update_arms")
        events.set_callback("update_arms", self.name, "update_arms")

        self.flipperstream = datastreams.get_stream("flipper")
        self.intakestream = datastreams.get_stream("intake")

        events.set_callback("enabled", self.name, "run")
        events.set_callback("disabled", self.name, "disable")



    def disable(self):
        self.stop_flag = True
        self.armstream.push(False, self.name, autolock=True)

    def run(self):
        self.stop_flag = False
        while not self.stop_flag:
            self.intake_motor.Set(float(self.intakestream.get(0)))
            self.flipper_solenoid.Set(not self.flipperstream.get(True))
            time.sleep(.05)
        print("Intake Stopped")

    def update_arms(self):
        if self.armstream.get(True):
            modmaster.get_mod("cannon").disable(self.name)
            self.arm_solenoid.Set(False)
        else:
            modmaster.get_mod("cannon").enable(self.name)
            self.arm_solenoid.Set(True)




