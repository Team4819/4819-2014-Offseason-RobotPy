__author__ = 'christian'
from framework import events, module_engine, wpiwrap
import time


class Module:
    subsystem = "debugging"
    stop_flag = False

    def __init__(self):
        self.joystick = wpiwrap.Joystick("Joystick 1", self.subsystem, 1)
        events.add_callback("run", self.subsystem, callback=self.run, inverse_callback=self.stop)

    def run(self):
        self.stop_flag = False
        last_reload_button = True
        while not self.stop_flag:
            reload_button = self.joystick.get_button(10)
            if reload_button and not last_reload_button:
                module_engine.reload_mods()
            last_reload_button = reload_button
            time.sleep(.2)

    def stop(self):
        self.stop_flag = True