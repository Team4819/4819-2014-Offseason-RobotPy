from framework.module_engine import ModuleBase

__author__ = 'christian'

from framework import events, datastreams, wpiwrap, module_engine
try:
    import wpilib
except ImportError:
    from pyfrc import wpilib
import time
import json
import logging

class Module(ModuleBase):

    subsystem = "dashboard"

    def module_load(self):
        wpilib.SmartDashboard.init()
        self.joystick1 = datastreams.get_stream("joystick1")
        self.joystick2 = datastreams.get_stream("joystick2")
        self.ultrasonic_stream = datastreams.get_stream("ultrasonic")
        self.autonomous_conf_stream = datastreams.get_stream("autonomous_config")
        events.set_callback("run", self.run, self.subsystem)
        wpilib.SmartDashboard.PutNumber("Auto Routine", 2)
        wpilib.SmartDashboard.PutNumber("1st Shoot Distance", 12)
        wpilib.SmartDashboard.PutNumber("2nd Shoot Distance", 7)
        wpilib.SmartDashboard.PutNumber("Distance from Tape", 3)
        wpilib.SmartDashboard.PutNumber("Start Position", 1)



    def run(self):
        last_auto_routine = 5
        while not self.stop_flag:
            try:
                wpiwrap.publish_values()
            except Exception as e:
                logging.error(e)
            default = {"buttons": (False, False, False, False, False, False, False, False, False, False), "axes": (0,0,0,0)}
            joy1string = json.dumps(self.joystick1.get(default))
            joy2string = json.dumps(self.joystick2.get(default))
            wpilib.SmartDashboard.PutString("joystick1", joy1string)
            wpilib.SmartDashboard.PutString("joystick2", joy2string)
            wpilib.SmartDashboard.PutNumber("Ultrasonic Sensor", self.ultrasonic_stream.get(0))

            auto_routine = wpilib.SmartDashboard.GetNumber("Auto Routine")
            if auto_routine != last_auto_routine:
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

                first_shot = wpilib.SmartDashboard.GetNumber("1st Shoot Distance")
                second_shot = wpilib.SmartDashboard.GetNumber("2nd Shoot Distance")
                distance_from_tape = wpilib.SmartDashboard.GetNumber("Distance from Tape")
                start_position = wpilib.SmartDashboard.GetNumber("Start Position")

                self.autonomous_conf_stream.push({"first_shot": first_shot, "second_shot": second_shot, "distance_from_tape": distance_from_tape, "start_position": start_position}, self.subsystem, autolock=True)



            time.sleep(.5)


