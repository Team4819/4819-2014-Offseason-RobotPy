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
        self.armstream.on_update("SetArms")
        events.set_callback("SetArms", self.name, "set_arms")

        self.flipperstream = datastreams.get_stream("flipper")
        self.flipperstream.on_update("SetFlipper")
        events.set_callback("SetFlipper", self.name, "set_flipper")

        events.set_callback("enabled", self.name, "run")
        events.set_callback("disabled", self.name, "disable")

        #Setup data stream for wheels
        self.intakestream = datastreams.get("intake")

    def disable(self):
        self.stop_flag = True
        self.arms_up()

    def run(self):
        self.stop_flag = False
        self.arms_up()
        self.set_flipper()
        while not self.stop_flag:
            self.intake_motor.Set(float(self.intakestream.get(0)))
            time.sleep(.05)
        print("Intake Stopped")

    def set_arms(self):
        if self.armstream.get(True):
            modmaster.get_mod("cannon").disable(self.name)
            self.arm_solenoid.Set(True)
        else:
            self.arm_solenoid.Set(False)
            time.sleep(.5)
            modmaster.get_mod("cannon").enable(self.name)

    def set_flipper(self):
        self.flipper_solenoid.Set(not self.flipperstream.get(True))

