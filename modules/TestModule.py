__author__ = 'christian'
import logging
from modules import ModBase
import time
from pyfrc import wpilib

class module(ModBase.module):

    name = "TestModule"

    def run(self):
        logging.info("Started TestModule!")
        print("Hello World from the point of a brand-new, shiny, module!")
        if wpilib.IsDisabled():
            logging.info("We Are Disabled")
        else:
            logging.info("We Are Enabled")
        time.sleep(10)
        logging.info("Stopped TestModule!")
