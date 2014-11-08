__author__ = 'christian'
from framework import events, datastreams
import time


class Module:

    subsystem = "autonomous"

    def __init__(self):
        self.navigator_config_stream = datastreams.get_stream("navigator.config")
        self.navigator_goals_stream = datastreams.get_stream("navigator.goals")
        self.navigator_status_stream = datastreams.get_stream("navigator.status")
        self.autonomous_config_stream = datastreams.get_stream("auto_config")
        events.add_callback("autonomous", self.subsystem, self.run)

    def run(self, task):
        #Configure the navigator and mark position
        self.navigator_config_stream.push({"max_values": [5, 2], "cycles_per_second": 60, "precision": .2}, self.subsystem, autolock=True)
        events.trigger_event("drivetrain.mark", self.subsystem)
        time.sleep(.05)

        #Get the autonomous config
        config = self.autonomous_config_stream.get({"distance_from_tape": 10})

        #Set the navigator's goal and let it run!
        self.navigator_goals_stream.push([(0, config["distance_from_tape"])], self.subsystem, autolock=True)
        events.start_event("navigator.run", self.subsystem)
        time.sleep(.05)

        #Wait for it to finish
        while task.active and self.navigator_status_stream.get(1) is 0:
            time.sleep(.5)

        #Stop it and check for errors
        events.stop_event("navigator.run", self.subsystem)
        if self.navigator_status_stream.get(1) is -1:
            raise Exception("Error in navigator execution")