__author__ = 'christian'
from framework import modbase, events, datastreams
import time

class Module(modbase.Module):

    name = "autonomous"

    def module_load(self):
        self.navigator_config = datastreams.get_stream("navigator.config", True)
        self.navigator_status = datastreams.get_stream("navigator.status", True)
        events.set_callback("autonomous", self.run, self.name)

    def run(self):

        events.trigger("navigator.mark", self.name)
        self.navigator_config.push({"mode": 1, "y-goal": 10, "max-speed": 1, "acceleration": 1, "iter-second": 100, "precision": 1}, self.name, autolock=True)
        events.set_event("navigator.run", self.name, True)
        time.sleep(.2)

        while not self.stop_flag and self.navigator_status.get(1) is 0:
            time.sleep(.5)

        events.set_event("navigator.run", self.name, False)
        events.trigger("navigator.stop", self.name)
        if self.navigator_status.get(1) is -1:
            raise Exception("Error in navigator execution")