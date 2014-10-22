from framework import events, wpiwrap
__author__ = 'christian'


class Module:
    subsystem = "compressor"

    def __init__(self):
        self.compressor = wpiwrap.Compressor("Compressor", self.subsystem, 14, 1)
        self.pressure_switch = wpiwrap.DigitalInput("Pressure Switch", self.subsystem, 6)
        events.add_callback("enabled", self.subsystem, callback=self.start, inverse_callback=self.stop)

    def start(self):
        self.compressor.set(True)

    def stop(self):
        self.compressor.set(False)

