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

from framework import module_engine, events, filesystem
from framework.record import recorder, playback

try:
    import wpilib
except ImportError:
    from pyfrc import wpilib


class RobotTrunk(wpilib.SimpleRobot):

    def __init__(self):
        super().__init__()
        filesystem.root_dir = os.path.dirname(os.path.realpath(__file__))
        filesystem.gen_paths()
        filesystem.init_logs()

        module_engine.load_startup_mods(os.path.join(filesystem.root_dir, "modules", "mods.conf"))
        #Toggle the run event
        events.start_event("run", "robot_main")

        recorder.startRecording()

        self.reaper = module_engine.Janitor()
        self.reaper.start()

    def Disabled(self):
        """Called when the robot is disabled"""
        events.start_event("disabled", "robot_main")
        while self.IsDisabled():
            self.reaper.delay_death()
            wpilib.Wait(0.1)
        events.stop_event("disabled", "robot_main")


    def Autonomous(self):
        """Called when autonomous mode is enabled"""
        events.start_event("enabled", "robot_main")
        events.start_event("autonomous", "robot_main")
        while self.IsAutonomous() and self.IsEnabled():
            self.reaper.delay_death()
            wpilib.Wait(0.1)
        events.stop_event("enabled", "robot_main")
        events.stop_event("autonomous", "robot_main")

    def OperatorControl(self):
        """Called when operation control mode is enabled"""
        events.start_event("enabled", "robot_main")
        events.start_event("teleoperated", "robot_main")
        while self.IsOperatorControl() and self.IsEnabled():
            self.reaper.delay_death()
            wpilib.Wait(0.04)
        events.stop_event("enabled", "robot_main")
        events.stop_event("teleoperated", "robot_main")

def run():
    """Main loop"""
    robot = RobotTrunk()
    robot.StartCompetition()
    return robot

if __name__ == '__main__':
    import physics
    wpilib.internal.physics_controller.setup(physics)
    wpilib.run()