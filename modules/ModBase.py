__author__ = 'christian'
import threading
import logging
import time

class module(threading.Thread):

    name = "ModuleBase"


    def run(self):
        print("started running module " + self.name)
        time.sleep(10)
        print("ended run of module " + self.name)
