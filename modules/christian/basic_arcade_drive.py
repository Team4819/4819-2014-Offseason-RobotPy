__author__ = 'christian'
from framework import modbase, events, datastreams, wpiwrap
import time


class Module(modbase.Module):

    name = "drivetrain"

    def module_load(self):
        self.left_motor = wpiwrap.Talon("left motor", self.name, 1)
        self.right_motor = wpiwrap.Talon("right motor", self.name, 2)

        events.set_callback("enabled", self.run, self.name)
        events.set_callback("disabled", self.stop, self.name)
        self.control_stream = datastreams.get_stream("drive")

    def run(self):
        self.stop_flag = False
        while not self.stop_flag:
            drive = self.control_stream.get((0, 0))

            output_left = drive[0] - drive[1]

            if abs(output_left) > 1:
                output_left = abs(output_left)/output_left

            output_right = drive[0] + drive[1]

            if abs(output_right) > 1:
                output_right = abs(output_right)/output_right

            self.left_motor.set(output_left)
            self.right_motor.set(output_right)

            time.sleep(.05)

    def stop(self):
        self.stop_flag = True