"""
This is the starting point for any RobotPy program, and is where robot code would normally be built.

Instead, we use this to start the framework and control robot state events, such as enabled, disabled,
 autonomous, or teleoperated.
"""

#This is a little setup to catch and log errors that crash the interpreter, shamelessly copied from
# the internet.

#Load just the minimum stuff to start with, so we hopefully won't crash before we have this hook in-place
import sys
import os
import traceback


def my_excepthook(type, value, tb):
    # you can log the exception to a file here
    message = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "death_message.log"), "a", 1)
    traceback.print_exception(type, value, tb, 100, message)
    message.close()

    # the following line does the default (prints it to err)
    sys.__excepthook__(type, value, tb)

sys.excepthook = my_excepthook

#Now we actually start doing things!
#----------------------------------

from framework import module_engine, events, filesystem

try:
    import wpilib
except ImportError:
    from pyfrc import wpilib


class RobotTrunk(wpilib.SimpleRobot):

    def __init__(self):
        #This is called on bot start-up. First we call the parent class's init function.
        super().__init__()

        #Get the logging stuff setup: figure out what the project directory is,
        # then calculate all of the paths and start the logs!
        filesystem.root_dir = os.path.dirname(os.path.realpath(__file__))
        filesystem.gen_paths()
        filesystem.init_logs()

        #Load all modules specified under "StartupMods" in the config file modules/mods.conf
        module_engine.load_startup_mods(os.path.join(filesystem.root_dir, "modules", "mods.conf"))

        #Start the run event
        events.start_event("run", "robot_main")

        #The janitor is a process who's job is to stop all of the modules when the main thread stops.
        # we basically call janitor.delay_death() every time we loop. If that function is not called in about 2 seconds,
        # all modules get automatically unloaded.
        self.janitor = module_engine.Janitor()
        self.janitor.start()

    def Disabled(self):
        """Called when the robot is disabled"""
        #Start the disabled event
        events.start_event("disabled", "robot_main")
        while self.IsDisabled():
            #Let the janitor know we are still alive.
            self.janitor.delay_death()
            wpilib.Wait(0.1)
        #Stop the disabled event
        events.stop_event("disabled", "robot_main")

    def Autonomous(self):
        """Called when autonomous mode is enabled"""
        #Start the enabled and autonomous events
        events.start_event("enabled", "robot_main")
        events.start_event("autonomous", "robot_main")
        while self.IsAutonomous() and self.IsEnabled():
            #Let the janitor know we are still alive.
            self.janitor.delay_death()
            wpilib.Wait(0.1)
        #Stop the autonomous and enabled events
        events.stop_event("enabled", "robot_main")
        events.stop_event("autonomous", "robot_main")

    def OperatorControl(self):
        """Called when operation control mode is enabled"""
        #Start the enabled and teleoperated events
        events.start_event("enabled", "robot_main")
        events.start_event("teleoperated", "robot_main")
        while self.IsOperatorControl() and self.IsEnabled():
            #Let the janitor know we are still alive.
            self.janitor.delay_death()
            wpilib.Wait(0.1)
        #Stop the enabled and teleoperated events
        events.stop_event("enabled", "robot_main")
        events.stop_event("teleoperated", "robot_main")


#This is the actual entry-point of the application.
def run():
    """Main loop"""
    robot = RobotTrunk()
    robot.StartCompetition()
    return robot

#This bit of code is used to configure pyfrc, if used.
if __name__ == '__main__':
    import physics
    wpilib.internal.physics_controller.setup(physics)
    wpilib.run()