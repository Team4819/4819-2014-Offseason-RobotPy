from framework import modmaster, modbase, datastreams, events, wpiwrap
import time
try:
    import wpilib
except ImportError:
    from pyfrc import wpilib
__author__ = 'christian'


class Module(modbase.Module):

    name = "intake"

    def module_load(self):

        #Get refrences
        self.arm_solenoid = wpiwrap.Solenoid("Arm Solenoid", self.name, 2)
        self.flipper_solenoid = wpiwrap.Solenoid("Flipper Solenoid", self.name, 1)
        self.intake_motor = wpiwrap.Talon("Intake Motor", self.name, 3)


        self.armstream = datastreams.get_stream("arms")
        self.armstream.on_update("update_arms")
        events.set_callback("update_arms", self.update_arms, self.name)

        self.flipperstream = datastreams.get_stream("flipper")
        self.intakestream = datastreams.get_stream("intake")

        events.set_callback("enabled", self.run, self.name)
        events.set_callback("disabled", self.disable, self.name)
        events.set_callback("cannon.load", self.refresh_cannon_disable, self.name)

    def refresh_cannon_disable(self):
        if self.armstream.get(True):
            modmaster.get_mod("cannon").disable(self.name)
        else:
            modmaster.get_mod("cannon").enable(self.name)

    def disable(self):
        self.stop_flag = True
        self.armstream.push(True, self.name, autolock=True)

    def run(self):
        self.stop_flag = False
        while not self.stop_flag:
            self.intake_motor.Set(float(self.intakestream.get(0)))
            self.flipper_solenoid.Set(not self.flipperstream.get(False))
            time.sleep(.05)

    def update_arms(self):
        if self.armstream.get(True):
            modmaster.get_mod("cannon").disable(self.name)
            self.arm_solenoid.Set(False)
        else:
            modmaster.get_mod("cannon").enable(self.name)
            self.arm_solenoid.Set(True)




