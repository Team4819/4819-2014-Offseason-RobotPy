__author__ = 'christian'
import logging
from modules import ModBase
import time
from pyfrc import wpilib

class module(ModBase.module):

    name = "TestModule"

    def run(self):
        print("Started TestModule!")
        print("Hello World from the point of a brand-new, shiny, module!")
        if wpilib.IsDisabled():
            print("We Are Disabled")
        else:
            print("We Are Enabled")
        time.sleep(10)
        print("Stopped TestModule!")
