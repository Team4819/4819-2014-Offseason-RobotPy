from framework import modmaster, events

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
        self.reaper = modmaster.GrimReaper()
        self.reaper.start()

    def Disabled(self):
        '''Called when the robot is disabled'''
        events.trigger("disabled", "RobotTrunk")
        while self.IsDisabled():
            self.reaper.delay_death()
            wpilib.Wait(0.1)

    def Autonomous(self):
        '''Called when autonomous mode is enabled'''
        events.trigger("enabled", "RobotTrunk")
        events.trigger("autonomous", "RobotTrunk")
        while self.IsAutonomous() and self.IsEnabled():
            self.reaper.delay_death()
            wpilib.Wait(0.1)

    def OperatorControl(self):
        '''Called when operation control mode is enabled'''
        events.trigger("enabled", "RobotTrunk")
        events.trigger("teleoperated", "RobotTrunk")
        while self.IsOperatorControl() and self.IsEnabled():
            self.reaper.delay_death()
            wpilib.Wait(0.04)


def run():
    """Main loop"""
    robot = RobotTrunk()
    robot.StartCompetition()
    return robot

if __name__ == '__main__':
    wpilib.run()