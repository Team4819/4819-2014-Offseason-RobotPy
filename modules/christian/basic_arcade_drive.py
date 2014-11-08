__author__ = 'christian'
from framework import events, wpiwrap, datastreams
import time


class Module:
    """This is a basic version of the drivetrain module, using pure estimation rather than sensors for state feedback"""

    subsystem = "drivetrain"
    current_distance = 0
    current_angle = 0
    current_speed = 0

    def __init__(self):
        self.joystick = wpiwrap.Joystick("Joystick 1", self.subsystem, 1)
        self.left_motor = wpiwrap.Talon("left motor", self.subsystem, 1)
        self.right_motor = wpiwrap.Talon("right motor", self.subsystem, 2)

        events.add_callback("enabled", self.subsystem, self.run_loop)
        events.add_callback("drivetrain.mark", self.subsystem, self.mark)

        self.state_stream = datastreams.get_stream("drivetrain.state")
        self.control_stream = datastreams.get_stream("drivetrain.control")

        self.current_distance = 0
        self.current_angle = 0

    def mark(self, task):
        self.current_distance = 0
        self.current_angle = 0

    def run_loop(self, task):
        """Listen to joystick input and the control datastream to determine what to do with the drivetrain"""
        while task.active:
            joystick_input_x = self.joystick.get_axis(0)
            joystick_input_y = self.joystick.get_axis(1)

            #Deadbands
            if abs(joystick_input_x) < .1:
                joystick_input_x = 0

            if abs(joystick_input_y) < .1:
                joystick_input_y = 0

            control_input = self.control_stream.get((0, 0))

            #Decide what input source to use
            if joystick_input_x is not 0 or joystick_input_y is not 0:
                #If we have any joystick input, use it. Also zero any existing control_input.
                if control_input[0] is not 0 or control_input[1] is not 0:
                    self.control_stream.push((0, 0), self.subsystem, autolock=True)
                input_y = joystick_input_y
                input_x = joystick_input_x
            else:
                #Otherwise use control_input
                input_y = control_input[1]/5
                input_x = control_input[0]/5

            output_left = input_x - input_y

            if abs(output_left) > 1:
                output_left = abs(output_left)/output_left

            output_right = input_x + input_y

            if abs(output_right) > 1:
                output_right = abs(output_right)/output_right

            self.left_motor.set(output_left)
            self.right_motor.set(output_right)

            self.current_distance += input_y * 8 * .05
            self.current_angle += input_x * 4 * .05
            self.current_speed = input_y * 8
            self.state_stream.push({"angle": self.current_angle, "distance": self.current_distance, "speed": self.current_speed}, self.subsystem, autolock=True)

            time.sleep(.05)

        self.left_motor.set(0)
        self.right_motor.set(0)