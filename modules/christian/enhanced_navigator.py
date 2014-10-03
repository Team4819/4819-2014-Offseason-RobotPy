__author__ = 'christian'
from framework import modbase, events, datastreams, wpiwrap
import logging
import time

class Module(modbase.Module):

    name = "navigator"



    default_config = {"mode": 0, "x-goal": 0, "y-goal": 0, "max-speed": 5, "acceleration": 3, "make-up": 1, "iter-second": 4, "precision": 1, "gyroscope": True}

    def module_load(self):
        self.running = False
        self.drive_stream = datastreams.get_stream("drive")
        self.config_stream = datastreams.get_stream("navigator.config")
        self.default_config.update(self.config_stream.get(dict()))
        self.status_stream = datastreams.get_stream("navigator.status")
        self.position_stream = datastreams.get_stream("position")
        events.set_callback("run", self.sensor_poll, self.name)
        events.set_callback("disabled", self.stop_drive, self.name)
        events.set_callback("navigator.run", self.do_drive, self.name)
        events.set_callback("navigator.stop", self.stop_drive, self.name)
        events.set_callback("navigator.mark", self.mark, self.name)
        self.right_encoder = wpiwrap.Encoder("Right Encoder", self.name, 1, 2)
        self.left_encoder = wpiwrap.Encoder("Left Encoder", self.name, 3, 4)
        self.gyroscope = wpiwrap.Gyro("Gyroscope", self.name, 2)
        self.current_x = 0
        self.current_y = 0
        self.current_speed_x = 0
        self.current_speed_y = 0
        self.current_accel_y = 0
        self.current_accel_x = 0
        self.last_x = 0
        self.last_y = 0
        self.last_out_x = 0
        self.last_out_y = 0
        self.last_speed_x = 0
        self.last_speed_y = 0
        self.last_accel_y = 0
        self.last_accel_x = 0
        self.stage = 0
        self.values_reset = False

    def sensor_poll(self):
        last_gyro = 0
        last_encoder = 0
        while not self.stop_flag:

            if not self.values_reset:
                encoder_value = self.left_encoder.get_rate()
                if (encoder_value - last_encoder)/.3 > 10:
                    raise Exception("Encoder is returning a scary value!")
                gyro_value = self.gyroscope.get()
                if (gyro_value - last_gyro)/.3 > 400:
                    raise Exception("Gyro is returning a scary value!")
                last_encoder = encoder_value
            else:
                self.values_reset = False
            last_gyro = gyro_value
            time.sleep(.3)

    def mark(self):
        self.current_x = 0
        self.current_y = 0
        self.left_encoder.Reset()
        self.right_encoder.Reset()
        #self.gyroscope.reset()
        self.values_reset = True

    def do_drive(self):
        self.status_stream.push(0, self.name, autolock=True)
        self.drive_stream.lock(self.name)
        self.running = True
        self.success = False
        config = self.default_config
        self.stage = 0
        self.last_encoder = 0

        try:
            while self.running and not self.success and not self.stop_flag:
                config.update(self.config_stream.get(self.default_config))
                self.position_stream.push((self.current_x, self.current_y), self.name, autolock=True)
                #TODO get something better here
                wait_time = 1/config["iter-second"]
                self.current_y = self.left_encoder.get()



                self.current_speed_y = self.left_encoder.get_rate()
                out_x = 0
                out_y = 0
                delta_y = config["y-goal"] - self.current_y
                move_mode = 0

                #Bang Bang Navigation
                if config["mode"] is 0:
                    sign = abs(delta_y)/delta_y
                    wanted_speed_y = sign * config["max-speed"]
                    speed_delta = wanted_speed_y - self.current_speed_y
                    if abs(speed_delta) > config["acceleration"]:
                        speed_delta = abs(speed_delta)/speed_delta * config["acceleration"]
                    accel_y = speed_delta
                    if delta_y < config["precision"]:
                        self.success = True
                        move_mode = 1

                #Acceleration
                if config["mode"] is 1:
                    sign = abs(delta_y)/delta_y
                    accel_y = sign * config["acceleration"]
                    if abs(self.last_speed_y) > config["precision"]:
                        speed_delta = abs(self.last_speed_y) - config["max-speed"]
                        if speed_delta > 0:
                            accel_y = - speed_delta * .1
                    if delta_y < config["precision"]:
                        self.success = True
                        move_mode = 1

                #Trapezoidial Motion Profile
                if config["mode"] is 2:

                    if self.stage is 2:
                        accel_y = -config["acceleration"]
                        if delta_y < config["precision"] or self.current_speed_y <= 0:
                            accel_y = 0
                            self.stage = 3
                            move_mode = 1

                    elif self.stage is 1:
                        accel_y = config["max-speed"] - self.current_speed_y
                        end_range = (self.current_speed_y * self.current_speed_y / (config["acceleration"] * 2))
                        if delta_y - end_range < config["precision"]:
                            self.stage = 2

                    elif self.stage is 0:
                        sign = abs(delta_y)/delta_y
                        accel_y = sign * config["acceleration"]
                        if abs(self.current_speed_y) >= config["max-speed"]:
                            accel_y = 0
                            self.stage = 1
                        end_range = (self.current_speed_y * self.current_speed_y / (config["acceleration"] * 2))
                        if delta_y - end_range < config["precision"]:
                            self.stage = 2

                    else:
                        self.success = True



                if move_mode is 0:
                    self.current_accel_y = (self.current_speed_y - self.last_speed_y) * wait_time

                    accel_err = accel_y - self.current_accel_y

                    if abs(accel_err) > config["make-up"]:
                        accel_err = abs(accel_err)/accel_err * config["make-up"]

                    out_y = self.last_out_y + (accel_err * wait_time)

                if config["gyroscope"]:
                    out_x = self.gyroscope.get()/-150

                if abs(out_y) > 1:
                    out_y = abs(out_y)/out_y

                if self.success:
                    out_x = 0
                    out_y = 0

                self.drive_stream.push((out_x, out_y), self.name)

                self.last_out_y = out_y
                self.last_out_x = out_x
                self.last_speed_y = self.current_speed_y
                self.last_speed_x = self.current_speed_x
                self.last_accel_y = self.current_accel_y
                self.last_accel_x = self.current_accel_x
                self.last_x = self.current_x
                self.last_y = self.current_y

                time.sleep(wait_time)
            self.status_stream.push(1, self.name, autolock=True)
        except datastreams.LockError:
            self.status_stream.push(-1, self.name, autolock=True)

    def stop_drive(self):
        self.running = False
        time.sleep(.1)
        try:
            self.drive_stream.push((0, 0), self.name)
        except datastreams.LockError:
            pass
        logging.info("I will stop doing something!")