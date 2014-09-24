__author__ = 'christian'
from framework import modbase, events, datastreams
import logging
import time


class Module(modbase.Module):

    name = "navigator"

    default_config = {"mode": 0, "x-goal": 0, "y-goal": 0, "max-speed": 1, "acceleration": 1, "iter-second": 4, "precision": 1}

    def module_load(self):
        self.running = False
        self.drive_stream = datastreams.get_stream("drive")
        self.config_stream = datastreams.get_stream("navigator.config")
        self.default_config.update(self.config_stream.get(dict()))
        self.status_stream = datastreams.get_stream("navigator.status")
        self.position_stream = datastreams.get_stream("position")
        events.set_callback("navigator.run", self.do_drive, self.name)
        events.set_callback("navigator.stop", self.stop_drive, self.name)
        events.set_callback("navigator.mark", self.mark, self.name)
        self.current_x = 0
        self.current_y = 0

    def mark(self):
        self.current_x = 0
        self.current_y = 0

    def do_drive(self):
        self.status_stream.push(0, self.name, autolock=True)
        self.drive_stream.lock(self.name)
        self.running = True
        self.success = False
        config = self.default_config
        runtime_vars = {"last_out_x": 0, "last_out_y": 0, "last_accel_x": 0, "last_accel_y": 0}
        try:
            while self.running and not self.success and not self.stop_flag:
                config.update(self.config_stream.get(self.default_config))
                self.position_stream.push((self.current_x, self.current_y), self.name, autolock=True)
                #TODO get something better here
                wait_time = 1/config["iter-second"]

                #Bang Bang Navigation
                if config["mode"] is 0:
                    out_x = 0
                    out_y = 0
                    delta_x = config["x-goal"] - self.current_x
                    delta_y = config["y-goal"] - self.current_y
                    self.success = True
                    if abs(delta_x) > config["precision"]:
                        sign = abs(delta_x)/delta_x
                        out_x = sign * config["max-speed"]
                        self.current_x += sign * 8 * wait_time * out_x
                        self.success = False

                    if abs(delta_y) > config["precision"]:
                        sign = abs(delta_y)/delta_y
                        out_y = sign * config["max-speed"]
                        self.current_y += 8 * wait_time * out_y
                        self.success = False

                    self.drive_stream.push((out_x, out_y), self.name)

                #Acceleration
                if config["mode"] is 1:
                    out_x = 0
                    out_y = 0
                    delta_x = config["x-goal"] - self.current_x
                    delta_y = config["y-goal"] - self.current_y
                    self.success = True

                    if abs(delta_x) > config["precision"]:
                        sign = abs(delta_x)/delta_x
                        out_x = runtime_vars["last_out_x"]
                        out_x += sign * config["acceleration"] * wait_time
                        if abs(out_x) < config["max-speed"]:
                            out_x = sign
                        self.current_x += 8 * wait_time * out_x
                        self.success = False

                    if abs(delta_y) > config["precision"]:
                        sign = abs(delta_y)/delta_y
                        out_y = runtime_vars["last_out_y"]
                        out_y += sign * config["acceleration"] * wait_time
                        if abs(out_y) >= config["max-speed"]:
                            out_y = sign
                        self.current_y += 8 * wait_time * out_y
                        self.success = False

                    runtime_vars["last_out_x"] = out_x
                    runtime_vars["last_out_y"] = out_y

                    self.drive_stream.push((out_x, out_y), self.name)

                #C Drive (Acceleration and Deceleration limits, otherwise maxed)
                if config["mode"] is 2:
                    out_x = 0
                    out_y = 0
                    delta_x = config["x-goal"] - self.current_x
                    delta_y = config["y-goal"] - self.current_y
                    self.success = True

                    if abs(delta_x) > config["precision"]:
                        sign = abs(delta_x)/delta_x

                        out_x = runtime_vars["last_out_x"]
                        out_x += sign * config["acceleration"] * wait_time
                        if abs(out_x) < config["max-speed"]:
                            out_x = sign
                        self.current_x += 8 * wait_time * out_x
                        self.success = False

                    if abs(delta_y) > config["precision"]:
                        sign = abs(delta_y)/delta_y
                        out_y = runtime_vars["last_out_y"]
                        out_y += sign * config["acceleration"] * wait_time
                        if abs(out_y) >= config["max-speed"]:
                            out_y = sign
                        self.current_y += 8 * wait_time * out_y
                        self.success = False

                    runtime_vars["last_accel_x"] = (out_x - runtime_vars["last_out_x"]) / wait_time
                    runtime_vars["last_accel_y"] = (out_y - runtime_vars["last_out_y"]) / wait_time

                    runtime_vars["last_out_x"] = out_x
                    runtime_vars["last_out_y"] = out_y

                    self.drive_stream.push((out_x, out_y), self.name)


                time.sleep(wait_time)
            self.status_stream.push(1, self.name, autolock=True)
        except datastreams.LockError:
            self.status_stream.push(-1, self.name, autolock=True)

    def stop_drive(self):
        self.running = False
        logging.info("I will stop doing something!")