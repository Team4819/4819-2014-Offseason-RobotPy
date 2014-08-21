__author__ = 'christian'
import threading
import logging
import time

class module(threading.Thread):

    name = "ModuleBase"


    def run(self):
        logging.info("started running module " + self.name)
        time.sleep(10)
        logging.info("ended run of module " + self.name)
