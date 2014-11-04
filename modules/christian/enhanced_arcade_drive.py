__author__ = 'christian'
from framework import events, wpiwrap, datastreams
import time


class Module:

    subsystem = "drivetrain"
    _stop_drive_loop = False
    _stop_state_loop = False

    def __init__(self):
        self.joystick = wpiwrap.Joystick("Joystick 1", self.subsystem, 1)
        self.left_motor = wpiwrap.Talon("left motor", self.subsystem, 1)
        self.right_motor = wpiwrap.Talon("right motor", self.subsystem, 2)

        self.right_encoder = wpiwrap.Encoder("Right Encoder", self.subsystem, 1, 2, 360, 20)
        self.left_encoder = wpiwrap.Encoder("Left Encoder", self.subsystem, 4, 3, 360, 20)
        self.gyroscope = wpiwrap.Gyro("Gyroscope", self.subsystem, 2, 300)

        events.add_callback("drivetrain.mark", self.subsystem, callback=self.mark)
        events.add_callback("enabled", self.subsystem, callback=self.drive_loop, inverse_callback=self.stop_drive_loop)
        events.add_callback("run", self.subsystem, callback=self.state_loop, inverse_callback=self.stop_state_loop)

        self.state_stream = datastreams.get_stream("drivetrain.state")
        self.control_stream = datastreams.get_stream("drivetrain.control")

    def mark(self):
        self.right_encoder.reset()
        self.left_encoder.reset()
        self.gyroscope.reset()

    def state_loop(self):
        """"Poll sensors to determine position, speed, direction, etc and send it to the state datastream"""
        self._stop_state_loop = False
        while not self._stop_state_loop:
            distance = self.right_encoder.get()
            speed = self.right_encoder.get_rate()
            angle = self.gyroscope.get()
            state = {"distance": distance, "speed": speed, "angle": angle}
            self.state_stream.push(state, self.subsystem, autolock=True)
            time.sleep(.05)

    def stop_state_loop(self):
        self._stop_state_loop = True

    def drive_loop(self):
        self._stop_drive_loop = False
        while not self._stop_drive_loop:
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

            time.sleep(.05)

        self.left_motor.set(0)
        self.right_motor.set(0)

    def stop_drive_loop(self):
        self._stop_drive_loop = True
        self.left_motor.set(0)
        self.right_motor.set(0)
