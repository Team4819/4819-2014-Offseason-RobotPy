#
# See the notes for the other physics sample
#


from pyfrc import wpilib
from pyfrc.physics import drivetrains


class PhysicsEngine(object):
    '''
        Simulates a motor moving something that strikes two limit switches,
        one on each end of the track. Obviously, this is not particularly
        realistic, but it's good enough to illustrate the point

        TODO: a better way to implement this is have something track all of
        the input values, and have that in a data structure, while also
        providing the override capability.
    '''

    def __init__(self, physics_controller):

        self.physics_controller = physics_controller

        self.position = 0
        self.last_distance = 0
        self.last_tm = None


    def update_sim(self, now, tm_diff):
        '''
            Called when the simulation parameters for the program need to be
            updated. This is mostly when wpilib.Wait is called.

            :param now: The current time as a float
            :param tm_diff: The amount of time that has passed since the last
                            time that this function was called
        '''

        # Simulate the drivetrain
        l_motor = wpilib.DigitalModule._pwm[0]
        r_motor = wpilib.DigitalModule._pwm[1]
        l_encoder = wpilib.DigitalModule._io[0]
        r_encoder = wpilib.DigitalModule._io[2]

        distance_traveled = (-self.physics_controller.get_position()[0]) - self.last_distance
        rate = (distance_traveled)/tm_diff
        if l_encoder.value is not None:
            l_encoder.value += distance_traveled
            l_encoder.rate = rate
            r_encoder.value += distance_traveled
            r_encoder.rate = rate
        self.last_distance += distance_traveled

        speed, rotation = drivetrains.two_motor_drivetrain(-l_motor.Get(), -r_motor.Get())
        self.physics_controller.drive(speed, rotation, tm_diff)

