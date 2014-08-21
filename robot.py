import logging
import ModMaster

from pyfrc import wpilib

class RobotTrunk(wpilib.SimpleRobot):

    modules = dict()

    def __init__(self):
        wpilib.SimpleRobot.__init__(self)

    def checkRestart():
        if stick1.GetRawButton(10):
            raise RuntimeError("Restart")


    def RobotMain(self):
        print("in robot main")
        ModMaster.loadMod("modules.TestModule")

    def StartCompetition(self):
        print("In StartCompetition!")
        ModMaster.loadMod("modules.TestModule")
        wpilib.SimpleRobot.StartCompetition(self)




def run():
    """Main loop"""
    robot = RobotTrunk()
    robot.StartCompetition()
    return robot

if __name__ == '__main__':
    wpilib.run(min_version='2014.4.0')