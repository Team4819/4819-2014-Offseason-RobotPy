__author__ = 'christian'
import logging
from modules import ModBase
import time
import ModMaster

class module(ModBase.module):

    name = "TestModule2"

    def run(self):
        print("Started TestModule!")
        print("Hello World from the point of a brand-new, shiny, 2nd module!")
        time.sleep(2)
        if ModMaster.getMod("TestModule").checkTrigger():
            print("Hey look, the trigger has been pulled!")
        else:
            print("Nope, not pulled")
        time.sleep(10)
        print("Stopped TestModule2!")
