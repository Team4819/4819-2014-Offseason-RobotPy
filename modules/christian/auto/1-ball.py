from framework.module_engine import ModuleBase

__author__ = 'christian'
from framework import events, datastreams
import time
try:
    import wpilib
except ImportError:
    from pyfrc import wpilib

class Module(ModuleBase):

    subsystem = "autonomous"

    def __init__(self):
        self.navigator_config = datastreams.get_stream("navigator.config")
        self.navigator_status = datastreams.get_stream("navigator.status")
        self.autonomous_config = datastreams.get_stream("auto_config")
        self.position_stream = datastreams.get_stream("position")
        self.arm_stream = datastreams.get_stream("arms")
        self.light_sensor_stream = datastreams.get_stream("light_sensor")
        events.add_callback("autonomous", self.subsystem, self.run)
        events.add_callback("disabled", self.subsystem, self.disable)


    def disable(self):
        self.stop_flag = True

    def run(self):
        self.stop_flag = False
        auto_start_time = time.time()

        config = self.autonomous_config.get({"first_shot": 12, "distance_from_tape": 3, "start_position": 1})
        #Drop Arms
        self.arm_stream.lock(self.subsystem)
        self.arm_stream.push(False, self.subsystem)

        #Trigger Vision
        wpilib.SmartDashboard.PutNumber("hot goal", 0)
        wpilib.SmartDashboard.PutBoolean("do vision", True)

        #Drive to line
        events.trigger_event("navigator.mark")
        self.navigator_config.push({"mode": 1, "y-goal": config["distance_from_tape"], "max-speed": 3, "acceleration": 5, "iter-second": 10, "make-up": 1.5, "precision": .1}, self.subsystem, autolock=True)
        events.set_event("navigator.run", self.subsystem, True)
        time.sleep(.2)
        start_time = time.time()
        while not self.stop_flag and self.navigator_status.get(1) is 0 and time.time() - start_time < 5 and self.light_sensor_stream.get(1.5) < 2.5:
            if self.stop_flag:
                return
            time.sleep(.5)
        if self.stop_flag: return
        self.stop_nav()

        #Fork for hot
        time.sleep(1)
        hot_goal = wpilib.SmartDashboard.GetNumber("hot goal")
        current_time_elapsed = time.time() - auto_start_time
        if config["start_position"] != hot_goal:
            sleep_time = 5 - current_time_elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)


        #Charge!

        shot_drive = 18 - config["first_shot"]

        events.trigger_event("navigator.mark")
        self.navigator_config.push({"mode": 1, "y-goal": shot_drive + 1, "max-speed": 5, "acceleration": 15, "iter-second": 10, "make-up": 1.5}, self.subsystem, autolock=True)
        events.set_event("navigator.run", self.subsystem, True)
        start_time = time.time()
        pos = self.position_stream.get((0, 0))
        while not self.stop_flag and self.navigator_status.get(1) is 0 and time.time() - start_time < 5 and abs(pos[1] - shot_drive) > 1:
            pos = self.position_stream.get((0, 0))
            if self.stop_flag:
                return
            time.sleep(.1)
        if self.stop_flag: return
        if self.navigator_status.get(1) is -1:
            raise Exception("Error in navigator execution")

        #Shoot
        events.trigger_event("highShot")

        #Wait for shooting to end
        time.sleep(.5)

        #STOP!!!
        self.stop_nav()



    def stop_nav(self):
        events.set_event("navigator.run", self.subsystem, False)
        events.trigger_event("navigator.stop")
        #if self.navigator_status.get(1) is -1:
        #    raise Exception("Error in navigator execution")


