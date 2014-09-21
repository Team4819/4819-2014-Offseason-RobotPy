__author__ = 'christian'
from framework import modbase, events, datastreams
import logging


class Module(modbase.Module):

    name = "navigator"

    def module_load(self):
        self.drive_stream = datastreams.get_stream("drive")
        events.set_callback("start_drive_sequence", self.do_drive, self.name)
        events.set_callback("stop_drive_sequence", self.stop_drive, self.name)

    def do_drive(self):
        logging.info("I will do something!")

    def stop_drive(self):
        logging.info("I will stop doing something!")