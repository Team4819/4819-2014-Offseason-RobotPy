__author__ = 'christian'
from framework import modbase, events, datastreams, refrence_db
import time
try:
    import wpilib
except ImportError:
    from pyfrc import wpilib


class Module(modbase.Module):

    name = "drivetrain"

    def module_load(self):
        self.left_motor = refrence_db.get_ref("left_motor", wpilib.Talon, 1)
        self.right_motor = refrence_db.get_ref("right_motor", wpilib.Talon, 2)

        events.set_callback("enabled", self.name, "run")
        events.set_callback("disabled", self.name, "stop")
        self.control_stream = datastreams.get_stream("drive")

    def run(self):
        self.stop_flag = False
        while not self.stop_flag:
            drive = self.control_stream.get((0, 0))

            output_left = drive[1] + drive[0]

            if output_left > 1:
                output_left = 1
            elif output_left < -1:
                output_left = -1

            output_right = drive[0] - drive[1]

            if output_right > 1:
                output_right = 1
            elif output_right < -1:
                output_right = -1

            self.left_motor.Set(output_left)
            self.right_motor.Set(output_right)

            time.sleep(.05)

    def stop(self):
        self.stop_flag = True