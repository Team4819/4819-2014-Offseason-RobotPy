import logging
import ModMaster
import time
try:
    import wpilib
except ImportError:
    from pyfrc import wpilib

class RobotTrunk(wpilib.SimpleRobot):


    def __init__(self):
        wpilib.SimpleRobot.__init__(self)
        ModMaster.loadMod("modules.TestModule")
        ModMaster.loadMod("modules.TestModule2")

    def __exit__(self):
        ModMaster.killAllMods()
        wpilib.SimpleRobot.__exit__(self)


    def OperatorControl(self):
        dog = self.GetWatchdog()
        dog.SetEnabled(True)
        dog.SetExpiration(0.25)

        while self.IsOperatorControl() and self.IsEnabled():
            dog.Feed()

            wpilib.Wait(0.04)



def run():
    """Main loop"""
    robot = RobotTrunk()
    robot.StartCompetition()
    return robot

if __name__ == '__main__':
    wpilib.run(min_version='2014.4.0')

