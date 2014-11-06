__author__ = 'christian'
from framework import events, datastreams, wpiwrap
import time
import logging
try:
    import wpilib
except ImportError:
    from pyfrc import wpilib


class Module:

    subsystem = "autonomous"
    stop_flag = False

    def __init__(self):
        #Get our datastreams
        self.navigator_config = datastreams.get_stream("navigator.config")
        self.navigator_goals = datastreams.get_stream("navigator.goals")
        self.navigator_status = datastreams.get_stream("navigator.status")
        self.autonomous_config = datastreams.get_stream("auto_config")
        self.drivetrain_state_stream = datastreams.get_stream("drivetrain.state")
        self.intake_stream = datastreams.get_stream("intake.control")

        #Setup Light sensor
        self.light_sensor = wpiwrap.AnalogInput("Light Sensor", self.subsystem, 1)

        #Register autonomous event callback
        events.add_callback("autonomous", self.subsystem, callback=self.run, inverse_callback=self.stop)

    class EndAutoError(Exception):
        """This is just a way to stop the autonomous routine at any time if we are told to"""
        pass

    def run(self):
        self.stop_flag = False
        auto_start_time = time.time()

        try:

            #Get auto config
            config = self.autonomous_config.get({"second_shot": 7, "first_shot": 12, "distance_from_tape": 3, "start_position": 1})

            #Configure navigator
            self.navigator_config.push({"max_values": [5, 5], "cycles_per_second": 10, "precision": .2}, self.subsystem, autolock=True)

            #Mark drivetrain
            events.trigger_event("drivetrain.mark", self.subsystem)

            #Drop Arms
            self.intake_stream.push({"arms_down": True, "flipper_out": True, "intake_motor": 0}, self.subsystem, autolock=True)

            #Trigger Vision
            wpilib.SmartDashboard.PutNumber("hot goal", 0)
            wpilib.SmartDashboard.PutBoolean("do vision", True)

            #Drive to line
            self.navigator_goals.push([(0, config["distance_from_tape"])], self.subsystem, autolock=True)
            events.start_event("navigator.run", self.subsystem)

            time.sleep(.2)
            start_time = time.time()
            #Loop until either we are told to stop, the navigator is done, it has taken too much time,
            # or the light sensor reports that we are on the line.
            while self.navigator_status.get(1) is 0 and time.time() - start_time < 5 and self.light_sensor.get() < 2.5:
                if self.stop_flag:
                    raise self.EndAutoError()
                time.sleep(.2)

            #Stop the bot
            events.stop_event("navigator.run", self.subsystem)

            #Wait a bit for things to settle
            time.sleep(1)

            #Check hot goal and wait if the goal we are on is cold
            hot_goal = wpilib.SmartDashboard.GetNumber("hot goal")
            if config["start_position"] != hot_goal:
                #How long do we sleep if we want to wake up at the 5 second mark of autonomous mode?
                sleep_time = time.time() - (5 + auto_start_time)
                if sleep_time > 0:
                    time.sleep(sleep_time)

            #Charge!

            #What is the target for our shot?
            current_distance = self.drivetrain_state_stream.get({"distance": 0})["distance"]
            shot_point = (18 - config["first_shot"]) + current_distance
            target_drive = (18 - config["second_shot"]) + current_distance

            self.navigator_goals.push([(0, target_drive)], self.subsystem, autolock=True)

            #Run navigator until we are at shot_point, then shoot and stop
            events.start_event("navigator.run", self.subsystem)
            start_time = time.time()
            pos = self.drivetrain_state_stream.get({"distance": 0})
            while self.navigator_status.get(1) is 0 and time.time() - start_time < 5 and abs(pos["distance"] - shot_point) > 1:
                pos = self.drivetrain_state_stream.get({"distance": 0})
                if self.stop_flag:
                    raise self.EndAutoError()
                time.sleep(.1)

            #Shoot
            events.trigger_event("shoot_cannon", self.subsystem)

            #Wait for shooting to end
            time.sleep(.5)

        except self.EndAutoError:
            pass

        #STOP!!!
        events.stop_event("navigator.run", self.subsystem)

    def stop(self):
        logging.info("Stopping autonomous")
        events.stop_event("navigator.run", self.subsystem)
        self.stop_flag = True



