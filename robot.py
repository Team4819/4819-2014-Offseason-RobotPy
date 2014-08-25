from framework import ModMaster

try:
    import wpilib
except ImportError:
    from pyfrc import wpilib

class RobotTrunk(wpilib.SimpleRobot):

    def __init__(self):
        super().__init__()
        self.reaper = ModMaster.GrimReaper()
        self.reaper.start()
        ModMaster.loadMod("modules.Joysticks")
        ModMaster.loadMod("modules.BasicArcadeDrive")
        ModMaster.loadMod("modules.Cannon")
        ModMaster.loadMod("modules.Intake")
        ModMaster.loadMod("modules.Compressor")

    def Disabled(self):
        '''Called when the robot is disabled'''
        ModMaster.setEvent("disabled")
        while self.IsDisabled():
            wpilib.Wait(0.1)
            self.reaper.delayDeath()

    def Autonomous(self):
        '''Called when autonomous mode is enabled'''
        ModMaster.setEvent("enabled")
        ModMaster.setEvent("autonomous")
        while self.IsAutonomous() and self.IsEnabled():
            wpilib.Wait(0.1)
            self.reaper.delayDeath()

    def OperatorControl(self):
        '''Called when operation control mode is enabled'''
        ModMaster.setEvent("enabled")
        ModMaster.setEvent("teleoperated")

        while self.IsOperatorControl() and self.IsEnabled():
            self.reaper.delayDeath()
            wpilib.Wait(0.04)


def run():
    """Main loop"""
    robot = RobotTrunk()
    robot.StartCompetition()
    return robot

if __name__ == '__main__':
    wpilib.run()