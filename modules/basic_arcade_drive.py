from framework import modbase, events, datastreams

__author__ = 'christian'
import time

try:
    import wpilib
except ImportError:
    from pyfrc import wpilib

class Module(modbase.Module):

    name = "drivetrain"

    def module_load(self):
        self.left_motor = wpilib.Talon(1)
        self.right_motor = wpilib.Talon(2)
        events.set_callback("enabled", self.name, "run")
        events.set_callback("disabled", self.name, "stop")
        self.control_stream = datastreams.get_stream("drive")
        super().module_load()

    def stop(self):
        self.stop_flag = True

    def run(self):
        self.stop_flag = False
        while not self.stop_flag:
            input_x = float(self.control_stream.get()[0])
            input_y = float(self.control_stream.get()[1])
            output_left = input_y + input_x
            if output_left > 1 or output_left < -1:
                output_left = 1
            output_right = input_y - input_x
            if output_right > 1 or output_right < -1:
                output_right = 1

            self.left_motor.Set(output_left)
            self.right_motor.Set(output_right)

            time.sleep(.05)
        print("BasicArcadeDrive stopped")
