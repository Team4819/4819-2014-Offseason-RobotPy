"""This is an example module, you can use this as a base when you go to create your own module."""
from framework import events
import time

##Need Wpilib? use this code snippit
#
#try:
#    import wpilib
#except ImportError:
#    from pyfrc import wpilib
from framework.module_engine import ModuleBase


class Module(ModuleBase):

    """This is the name used for module communication and logging.
     this should be the name of the subsystem, eg: 'drivetrain' or 'compressor' """
    subsystem = "hello world"


    def module_load(self):
        """This is run upon module load, initialize any variables or interfaces here, and subscribe to any events"""

        #This sets the method "self.do_stuff" to be run upon the event "run".
        #   The "run" event is triggered automatically, and should be used to start any loops
        #   designed to be run while the module is loaded
        events.set_callback("run", self.do_stuff, self.subsystem)

    def do_stuff(self):
        """This is a simple run loop that says 'Hello World!' every second until the module is told to terminate."""

        #IMPORTANT! All loops that will run indefinitely MUST watch for self.stop_flag. When this is true, YOU MUST STOP!
        while not self.stop_flag:
            print("Hello World!")
            time.sleep(1)
