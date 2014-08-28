from framework import modbase, events, datastreams, refrence_db

__author__ = 'christian'
import time

try:
    import wpilib
except ImportError:
    from pyfrc import wpilib

class Module(modbase.Module):

    name = "drivetrain"

    def module_load(self):
        self.left_motor = refrence_db.get_ref("left_motor")
        if self.left_motor is None:
            self.left_motor = wpilib.Talon(1)
            refrence_db.save_refrence(self.left_motor, "left_motor")

        self.right_motor = refrence_db.get_ref("right_motor")
        if self.right_motor is None:
            self.right_motor = wpilib.Talon(2)
            refrence_db.save_refrence(self.right_motor, "right_motor")

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

            self.left_motor.ref.Set(output_left)
            self.right_motor.ref.Set(output_right)

            time.sleep(.05)
        print("BasicArcadeDrive stopped")