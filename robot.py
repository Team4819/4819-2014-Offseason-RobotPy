import logging
import ModMaster
import time
try:
    import wpilib
except ImportError:
    from pyfrc import wpilib

class RobotTrunk(wpilib.IterativeRobot):


    def RobotInit(self):
        ModMaster.loadMod("modules.TestModule")

    def __exit__(self):
        ModMaster.killAllMods()
        wpilib.IterativeRobot.__exit__(self)





def run():
    """Main loop"""
    robot = RobotTrunk()
    robot.StartCompetition()
    return robot

if __name__ == '__main__':
    wpilib.run(min_version='2014.4.0')