"""
    This is an example module, it just sits there shouting out "Hello World!" at anybody who will listen.
    Very annoying.
"""
from framework import events
import time


class Module:

    """This is the name used for module communication and logging.
     this should be the name of the subsystem, eg: 'drivetrain' or 'compressor' """
    subsystem = "helloworld"

    def __init__(self):
        """This is run upon module load, initialize any variables or interfaces here, and subscribe to any events"""

        #This sets the method "do_stuff" to be run upon the event "run".
        #
        #   The "run" event is started automatically, and should be used to start any loops
        #   designed to be run constantly while the module is loaded.
        events.add_callback("disabled", self.subsystem, self.do_stuff)

    def do_stuff(self, task):
        """This is a simple run loop that says 'Hello World!' every second until the module is told to terminate."""
        #IMPORTANT! Any event-driven function that runs an infinite loop MUST listen to callback.active!
        while task.active:
            print("Hello World!")
            time.sleep(1)

