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

        speed, rotation = drivetrains.two_motor_drivetrain(4, l_motor, r_motor)
        self.physics_controller.drive(speed, rotation)

