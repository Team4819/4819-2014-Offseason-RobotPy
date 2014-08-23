__author__ = 'christian'
import logging
from modules import ModBase
import time
try:
    import wpilib
except ImportError:
    from pyfrc import wpilib

class module(ModBase.module):

    name = "TestModule"

    def __init__(self):
        self.stick = wpilib.Joystick(1)
        ModBase.module.__init__(self)

    def run(self):
        print("Started TestModule!")
        print("Hello World from the point of a brand-new, shiny, module!")
        stop = False
        while not stop:
            if self.stick.GetRawButton(10):
                print("We Are Pressed")
            else:
                print("We Are Not Pressed")
            time.sleep(2)
            stop = self.stick.GetRawButton(9) or self._stop.is_set()

        print("Stopped TestModule!")

    def checkTrigger(self):
        return self.stick.GetRawButton(10)
