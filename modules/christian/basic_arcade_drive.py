__author__ = 'christian'
from framework import events, wpiwrap, datastreams
import time


class Module:

    subsystem = "drivetrain"
    stop_flag = False

    def __init__(self):
        self.joystick = wpiwrap.Joystick("Joystick 1", self.subsystem, 1)
        self.left_motor = wpiwrap.Talon("left motor", self.subsystem, 1)
        self.right_motor = wpiwrap.Talon("right motor", self.subsystem, 2)

        events.add_callback("teleoperated", self.subsystem, callback=self.run, inverse_callback=self.stop)
        events.add_callback("drivetrain.mark", self.subsystem, callback=self.mark)

        self.position_stream = datastreams.get_stream("position")

        self.current_distance = 0
        self.current_angle = 0

    def mark(self):
        self.current_distance = 0
        self.current_angle = 0

    def run(self):
        self.stop_flag = False
        while not self.stop_flag:
            input_y = self.joystick.get_axis(0)
            input_x = self.joystick.get_axis(1)

            #Deadbands
            if abs(input_x) < .1:
                input_x = 0

            if abs(input_y) < .1:
                input_y = 0

            output_left = input_y - input_x

            if abs(output_left) > 1:
                output_left = abs(output_left)/output_left

            output_right = input_y + input_x

            if abs(output_right) > 1:
                output_right = abs(output_right)/output_right

            self.left_motor.set(output_left)
            self.right_motor.set(output_right)

            self.current_distance += input_y * 8 * .05
            self.current_angle += input_x * 4 * .05
            self.position_stream.push({"angle": self.current_angle, "distance": self.current_distance}, self.subsystem, autolock=True)

            time.sleep(.05)

    def stop(self):
        self.stop_flag = True
        self.left_motor.set(0)
        self.right_motor.set(0)