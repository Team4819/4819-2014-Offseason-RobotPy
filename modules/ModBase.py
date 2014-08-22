__author__ = 'christian'
import threading
import logging
import time

class module(threading.Thread):

    name = "ModuleBase"

    def __init__(self):
        threading.Thread.__init__(self)
        self._stop = threading.Event()

    def stop(self):
        self._stop.set()


    def run(self):
        print("started running module " + self.name)
        time.sleep(10)
        print("ended run of module " + self.name)
