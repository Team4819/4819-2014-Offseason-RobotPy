"""
    This is an example module, it just sits there shouting out "Hello World!" at anybody who will listen.
    Very annoying.
"""
from framework import events
import time


class Module:

    """This is the name used for module communication and logging.
     this should be the name of the subsystem, eg: 'drivetrain' or 'compressor' """
    subsystem = "hello world"

    #The variable we are going to use to stop the do_stuff loop
    stop_flag = False

    def __init__(self):
        """This is run upon module load, initialize any variables or interfaces here, and subscribe to any events"""

        #This sets the method "self.do_stuff" to be run upon the event "run".
        #
        #   The "run" event is started automatically, and should be used to start any loops
        #   designed to be run while the module is loaded.
        #
        #   It also sets the function stop_doing_stuff as the inverse callback. It will be called when the
        #   "run" event is stopped.

        events.add_callback("run", self.subsystem, callback=self.do_stuff, inverse_callback=self.stop_doing_stuff)

    def do_stuff(self):
        """This is a simple run loop that says 'Hello World!' every second until the module is told to terminate."""
        self.stop_flag = False

        #IMPORTANT! Any event-driven function that runs an infinite loop MUST have an inverse_callback setup that stops the loop!
        while not self.stop_flag:
            print("Hello World!")
            time.sleep(1)

    def stop_doing_stuff(self):
        self.stop_flag = True
