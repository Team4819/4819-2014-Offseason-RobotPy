__author__ = 'christian'
from framework import modbase, events, datastreams
import time

class Module(modbase.Module):

    subsystem = "autonomous"

    def module_load(self):
        self.navigator_config = datastreams.get_stream("navigator.config", True)
        self.navigator_status = datastreams.get_stream("navigator.status", True)
        self.autonomous_config = datastreams.get_stream("auto_config")
        events.set_callback("autonomous", self.run, self.subsystem)
        events.set_callback("disabled", self.disabled, self.subsystem)

    def disabled(self):
        self.stop_flag = True

    def run(self):
        self.stop_flag = False
        config = self.autonomous_config.get({"distance_from_tape": 5})
        events.trigger("navigator.mark", self.subsystem)
        self.navigator_config.push({"mode": 2, "y-goal": config["distance_from_tape"], "max-speed": 2, "acceleration": 2, "iter-second": 10, "precision": 1}, self.subsystem, autolock=True)
        events.set_event("navigator.run", self.subsystem, True)
        time.sleep(.2)

        while not self.stop_flag and self.navigator_status.get(1) is 0:
            time.sleep(.5)

        events.set_event("navigator.run", self.subsystem, False)
        events.trigger("navigator.stop", self.subsystem)
        if self.navigator_status.get(1) is -1:
            raise Exception("Error in navigator execution")
