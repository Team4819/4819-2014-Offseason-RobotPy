__author__ = 'christian'
from framework import events, datastreams, wpiwrap, module_engine
try:
    import wpilib
except ImportError:
    from pyfrc import wpilib
import time
import logging
import traceback


class Module:
    """This manages the smart dashboard output and autonomous selection"""

    subsystem = "dashboard"
    stop_flag = False

    def __init__(self):
        wpilib.SmartDashboard.init()

        #Initialize the ultra sonic sensor here
        self.ultrasonic = wpiwrap.Counter("Ultrasonic_Sensor", self.subsystem, 11)
        self.ultrasonic.set_semi_period()

        #Get datastream for autonomous config
        self.autonomous_conf_stream = datastreams.get_stream("autonomous_config")

        #Initialize smart dashboard variables
        wpilib.SmartDashboard.PutNumber("Auto Routine", 2)
        wpilib.SmartDashboard.PutNumber("1st Shoot Distance", 12)
        wpilib.SmartDashboard.PutNumber("2nd Shoot Distance", 7)
        wpilib.SmartDashboard.PutNumber("Distance from Tape", 3)
        wpilib.SmartDashboard.PutNumber("Start Position", 1)

        #Register callback
        events.add_callback("run", self.subsystem, callback=self.run, inverse_callback=self.stop)

    def run(self):
        last_auto_routine = 5
        self.stop_flag = False
        while not self.stop_flag:
            #Use wpiwrap's function to automatically report all sensor values
            try:
                wpiwrap.publish_values()
            except Exception as e:
                logging.error("Error: " + str(e) + "\n" + traceback.format_exc())

            #Manage autonomous routine selection and configuration
            auto_routine = wpilib.SmartDashboard.GetNumber("Auto Routine")
            if auto_routine != last_auto_routine:
                #If auto_routine has changed, load the appropriate autonomous module
                if auto_routine == 0:
                    try:
                        module_engine.get_modules("autonomous").load("modules.christian.auto.dead_auto")
                    except module_engine.ModuleUnloadError:
                        pass

                elif auto_routine == 3:
                    try:
                        module_engine.get_modules("autonomous").load("modules.christian.auto.stupid_auto")
                    except (module_engine.ModuleUnloadError, module_engine.ModuleLoadError) as e:
                        logging.error(e)

                elif auto_routine == 1:
                    try:
                        module_engine.get_modules("autonomous").load("modules.christian.auto.1-ball")
                    except (module_engine.ModuleUnloadError, module_engine.ModuleLoadError) as e:
                        logging.error(e)

                elif auto_routine == 2:
                    try:
                        module_engine.get_modules("autonomous").load("modules.christian.auto.2-ball")
                    except (module_engine.ModuleUnloadError, module_engine.ModuleLoadError) as e:
                        logging.error(e)

                last_auto_routine = auto_routine

                #Get all of the config values from the dashboard and send them to the autonomous config datastream.

                first_shot = wpilib.SmartDashboard.GetNumber("1st Shoot Distance")
                second_shot = wpilib.SmartDashboard.GetNumber("2nd Shoot Distance")
                distance_from_tape = wpilib.SmartDashboard.GetNumber("Distance from Tape")
                start_position = wpilib.SmartDashboard.GetNumber("Start Position")

                data = {"first_shot": first_shot, "second_shot": second_shot, "distance_from_tape": distance_from_tape, "start_position": start_position}
                self.autonomous_conf_stream.push(data, self.subsystem, autolock=True)

            time.sleep(.5)

    def stop(self):
        self.stop_flag = True


