from framework import events, wpiwrap
__author__ = 'christian'


class Module:
    subsystem = "compressor"

    def __init__(self):
        self.compressor = wpiwrap.Compressor("Compressor", self.subsystem, 14, 1)
        self.pressure_switch = wpiwrap.DigitalInput("Pressure Switch", self.subsystem, 6)
        events.add_callback("enabled", self.subsystem, self.start)
        events.add_inverse_callback("enabled", self.subsystem, self.stop)

    def start(self, task):
        self.compressor.set(True)

    def stop(self, task):
        self.compressor.set(False)

