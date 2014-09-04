from framework import modmaster, events
from framework.record import recorder, playback

try:
    import wpilib
except ImportError:
    from pyfrc import wpilib
try:
    import manhole
    manhole.install()
except ImportError:
    pass


class RobotTrunk(wpilib.SimpleRobot):

    def __init__(self):
        super().__init__()
        modmaster.load_startup_mods()
        recorder.startRecording()
        #playback.replay_recording()
        self.reaper = modmaster.GrimReaper()
        self.reaper.start()

    def Disabled(self):
        '''Called when the robot is disabled'''
        events.set_event("disabled", "RobotTrunk", True)
        while self.IsDisabled():
            self.reaper.delay_death()
            wpilib.Wait(0.1)
        events.set_event("disabled", "RobotTrunk", False)

    def Autonomous(self):
        '''Called when autonomous mode is enabled'''
        events.set_event("enabled", "RobotTrunk", True)
        events.set_event("autonomous", "RobotTrunk", True)
        while self.IsAutonomous() and self.IsEnabled():
            self.reaper.delay_death()
            wpilib.Wait(0.1)
        events.set_event("enabled", "RobotTrunk", False)
        events.set_event("autonomous", "RobotTrunk", False)

    def OperatorControl(self):
        '''Called when operation control mode is enabled'''
        events.set_event("enabled", "RobotTrunk", True)
        events.set_event("autonomous", "RobotTrunk", True)
        while self.IsOperatorControl() and self.IsEnabled():
            self.reaper.delay_death()
            wpilib.Wait(0.04)
        events.set_event("enabled", "RobotTrunk", False)
        events.set_event("teleoperated", "RobotTrunk", False)

def run():
    """Main loop"""
    robot = RobotTrunk()
    robot.StartCompetition()
    return robot

if __name__ == '__main__':
    import physics
    wpilib.internal.physics_controller.setup(physics)
    wpilib.run()