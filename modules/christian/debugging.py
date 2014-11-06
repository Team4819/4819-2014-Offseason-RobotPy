__author__ = 'christian'
from framework import events, module_engine, wpiwrap
import time


class Module:
    """This module contains various debugging utilities (currently 1) bound to joystick buttons."""
    subsystem = "debugging"
    stop_flag = False

    def __init__(self):
        self.joystick = wpiwrap.Joystick("Joystick 1", self.subsystem, 1)
        events.add_callback("run", self.subsystem, callback=self.run, inverse_callback=self.stop)

    def run(self):
        self.stop_flag = False
        #Initializing this to true to avoid a perpetual loop when this module gets reloaded!
        last_reload_button = True
        while not self.stop_flag:
            #If the reload button is pressed, reload all modules.
            reload_button = self.joystick.get_button(10)
            if reload_button and not last_reload_button:
                module_engine.reload_mods()

            #Save value and sleep
            last_reload_button = reload_button
            time.sleep(.5)

    def stop(self):
        self.stop_flag = True