from framework import modbase, events, datastreams, moderrors
from framework.refrence_db import get_ref

__author__ = 'christian'
import time

try:
    import wpilib
except ImportError:
    from pyfrc import wpilib

class Module(modbase.Module):

    name = "drivetrain"

    def module_load(self):

        self.left_motor = get_ref("left_motor")
        if self.left_motor.ref is None:
            self.left_motor.ref = wpilib.Talon(1)

        self.right_motor = get_ref("right_motor")
        if self.right_motor.ref is None:
            self.right_motor.ref = wpilib.Talon(2)

        events.set_callback("enabled", self.name, "run")
        events.set_callback("disabled", self.name, "stop")
        self.control_stream = datastreams.get_stream("drive")
        super().module_load()



    def stop(self):
        self.stop_flag = True

    def run(self):
        self.stop_flag = False

        while not self.stop_flag:
            drive = self.control_stream.get((0, 0))
            output_left = drive[1] + drive[0]
            if output_left > 1 or output_left < -1:
                output_left = 1
            output_right = drive[1] - drive[0]
            if output_right > 1 or output_right < -1:
                output_right = 1

                    #DIE!!!!!!
            if output_left is not output_right:
                raise moderrors.ModuleLoadError(self.name, "I HATE YOU!!!")

            self.left_motor.ref.Set(output_left)
            self.right_motor.ref.Set(output_right)

            time.sleep(.05)
        print("BasicArcadeDrive stopped")

    def module_unload(self):
        pass