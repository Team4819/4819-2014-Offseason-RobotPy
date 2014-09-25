__author__ = 'christian'
from framework import modbase, events, datastreams
import time

class Module(modbase.Module):

    name = "autonomous"

    def module_load(self):
        self.navigator_config = datastreams.get_stream("navigator.config", True)
        self.navigator_status = datastreams.get_stream("navigator.status", True)
        self.autonomous_config = datastreams.get_stream("auto_config")
        self.position_stream =  datastreams.get_stream("position")
        self.arm_stream = datastreams.get_stream("arms")
        self.intake_stream = datastreams.get_stream("intake")
        self.ball_presence_stream = datastreams.get_stream("ballpresence")
        events.set_callback("autonomous", self.run, self.name)

    def run(self):

        #Drop Arms
        self.arm_stream.lock(self.name)
        self.arm_stream.push(False, self.name)

        #Drive to line
        events.trigger("navigator.mark", self.name)
        self.navigator_config.push({"mode": 1, "y-goal": 3, "max-speed": 1, "acceleration": 1, "iter-second": 10, "precision": 1}, self.name, autolock=True)
        events.set_event("navigator.run", self.name, True)
        time.sleep(.2)
        start_time = time.clock()
        while not self.stop_flag and self.navigator_status.get(1) is 0 and time.clock() - start_time < 5:
            time.sleep(.5)

        events.set_event("navigator.run", self.name, False)
        events.trigger("navigator.stop", self.name)
        if self.navigator_status.get(1) is -1:
            raise Exception("Error in navigator execution")

        #Wait at line
        time.sleep(5)


        #Charge
        events.trigger("navigator.mark", self.name)
        self.navigator_config.push({"mode": 1, "y-goal": 15, "max-speed": .5, "acceleration": 1, "iter-second": 10, "precision": 1}, self.name, autolock=True)
        events.set_event("navigator.run", self.name, True)
        start_time = time.clock()
        pos = self.position_stream.get((0, 0))
        while not self.stop_flag and self.navigator_status.get(1) is 0 and time.clock() - start_time < 5 and abs(pos[1] - 8) > 1:
            pos = self.position_stream.get((0, 0))
            time.sleep(.2)
        if self.navigator_status.get(1) is -1:
            raise Exception("Error in navigator execution")

        #Shoot
        events.trigger("highShot", self.name)

        #Run intake
        self.intake_stream.lock(self.name)
        self.intake_stream.push(.5, self.name, True)

        #Wait for finish of drive arc
        while not self.stop_flag and self.navigator_status.get(1) is 0 and time.clock() - start_time < 7:
            time.sleep(.5)
        events.set_event("navigator.run", self.name, False)
        events.trigger("navigator.stop", self.name)
        if self.navigator_status.get(1) is -1:
            raise Exception("Error in navigator execution")

        #wait for ball presence
        while not self.stop_flag and not self.ball_presence_stream.get(False):
            time.sleep(.5)

        #Shoot
        events.trigger("highShot", self.name)

        #stop intake
        self.intake_stream.push(0, self.name)






