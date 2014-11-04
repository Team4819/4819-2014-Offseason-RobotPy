__author__ = 'christian'
from framework import events, datastreams
import time
import math
import logging


class Module:

    subsystem = "navigator"

    #Navigator Config dictionary:
    #max-speed: The maximum desired values for speed, acceleration, jerk, and so on
    #iter-second: The speed in iterations per second of the navigation loop
    #precision: The distance from the end goal to be in order to finish

    default_config = {"max_values": (5, 3, 5), "cycles_per_second": 4, "precision": 1}

    #Navigator goals:
    #This is a list of (x, y) values used as target coordinates
    default_goals = [(0, 0)]

    #Should we stop the loop?
    stop_loop = False

    def __init__(self):
        self.config_stream = datastreams.get_stream("navigator.config")
        self.goals_stream = datastreams.get_stream("navigator.goals")
        self.status_stream = datastreams.get_stream("navigator.status")
        self.drivetrain_state_stream = datastreams.get_stream("drivetrain.state")
        self.drivetrain_control_stream = datastreams.get_stream("drivetrain.control")

        events.add_callback("navigator.run", self.subsystem, callback=self.do_drive, inverse_callback=self.stop_drive)

    def do_drive(self):
        """Perform the currently-configured drive sequence"""

        try:
            #Set run status
            self.status_stream.push(0, self.subsystem, autolock=True)

            #Reset stop_loop flag
            self.stop_loop = False

            #Get configs
            config = self.default_config
            config.update(self.config_stream.get(self.default_config))
            goals = self.goals_stream.get(self.default_goals)

            logging.info("Navigating to point {}".format(goals[0]))

            self.drivetrain_control_stream.lock(self.subsystem)

            wait_time = 1/config["cycles_per_second"]

            last_speed = 0

            while not self.stop_loop:

                drivetrain_state = self.drivetrain_state_stream.get({"distance": 0, "speed": 0, "angle": 0})

                #How much farther do we have to go?
                distance_error = goals[0][1] - drivetrain_state["distance"]

                #Are we done? Then break!
                if abs(distance_error) < config["precision"]:
                    break

                #Calculate the approximate distance it will take to slow down
                slow_point = (drivetrain_state["speed"] ** 2 / (config["max_values"][1] * 2))

                #Calculate what speed we currently want to go at:
                wanted_speed = math.copysign(config["max_values"][0], distance_error)
                if distance_error < slow_point:
                    #We must slow down then!
                    wanted_speed = 0

                #Limit the acceleration
                wanted_speed_delta = wanted_speed - last_speed
                wanted_acceleration = math.copysign(config["max_values"][1], wanted_speed_delta)
                result_speed = last_speed + wanted_acceleration * wait_time

                #Add a bit of angle correction
                angle_component = - drivetrain_state["angle"] * .01

                #Send values to drivetrain
                self.drivetrain_control_stream.push((angle_component, result_speed), self.subsystem)

                last_speed = result_speed

                #Sleep until next loop
                time.sleep(wait_time)

            #Clean up
            self.drivetrain_control_stream.push((0, 0), self.subsystem)
            self.status_stream.push(1, self.subsystem, autolock=True)
        except datastreams.LockError:
            self.status_stream.push(-1, self.subsystem, autolock=True)

    def stop_drive(self):
        self.stop_loop = True