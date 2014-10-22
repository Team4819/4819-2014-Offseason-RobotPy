from framework.module_engine import ModuleBase

__author__ = 'christian'
from framework import events, datastreams
import time

class Module(ModuleBase):

    subsystem = "autonomous"

    def __init__(self):
        self.navigator_config = datastreams.get_stream("navigator.config")
        self.navigator_status = datastreams.get_stream("navigator.status")
        self.autonomous_config = datastreams.get_stream("auto_config")
        events.add_callback("autonomous", self.subsystem, self.run)
        events.add_callback("disabled", self.subsystem, self.disabled)

    def disabled(self):
        self.stop_flag = True

    def run(self):
        self.stop_flag = False
        config = self.autonomous_config.get({"distance_from_tape": 5})
        events.trigger_event("navigator.mark")
        self.navigator_config.push({"mode": 2, "y-goal": config["distance_from_tape"], "max-speed": 2, "acceleration": 2, "iter-second": 10, "precision": 1}, self.subsystem, autolock=True)
        events.set_event("navigator.run", self.subsystem, True)
        time.sleep(.2)

        while not self.stop_flag and self.navigator_status.get(1) is 0:
            time.sleep(.5)

        events.set_event("navigator.run", self.subsystem, False)
        events.trigger_event("navigator.stop")
        if self.navigator_status.get(1) is -1:
            raise Exception("Error in navigator execution")
