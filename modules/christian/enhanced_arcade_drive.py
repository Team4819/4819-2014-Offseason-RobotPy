__author__ = 'christian'
from framework import events, wpiwrap, datastreams
import time


class Module:

    subsystem = "drivetrain"
    _stop_drive = False
    _stop_position = False

    def __init__(self):
        self.joystick = wpiwrap.Joystick("Joystick 1", self.subsystem, 1)
        self.left_motor = wpiwrap.Talon("left motor", self.subsystem, 1)
        self.right_motor = wpiwrap.Talon("right motor", self.subsystem, 2)

        self.right_encoder = wpiwrap.Encoder("Right Encoder", self.subsystem, 1, 2, 360, 20)
        self.left_encoder = wpiwrap.Encoder("Left Encoder", self.subsystem, 4, 3, 360, 20)
        self.gyroscope = wpiwrap.Gyro("Gyroscope", self.subsystem, 2, 300)

        events.add_callback("drivetrain.mark", self.subsystem, callback=self.mark)
        events.add_callback("teleoperated", self.subsystem, callback=self.drive_loop, inverse_callback=self.stop_drive_loop)
        events.add_callback("run", self.subsystem, callback=self.position_loop, inverse_callback=self.stop_position_loop)

        self.position_stream = datastreams.get_stream("position")

    def mark(self):
        self.right_encoder.reset()
        self.left_encoder.reset()
        self.gyroscope.reset()

    def position_loop(self):
        self._stop_position = False
        while not self._stop_position:
            distance = self.right_encoder.get()
            angle = self.gyroscope.get()
            self.position_stream.push({"angle": angle, "distance": distance}, self.subsystem, autolock=True)
            time.sleep(.05)

    def stop_position_loop(self):
        self._stop_position = True

    def drive_loop(self):
        self._stop_drive = False
        while not self._stop_drive:
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

            time.sleep(.05)

        self.left_motor.set(0)
        self.right_motor.set(0)

    def stop_drive_loop(self):
        self._stop_drive = True
        self.left_motor.set(0)
        self.right_motor.set(0)
