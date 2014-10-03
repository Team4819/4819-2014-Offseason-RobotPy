__author__ = 'christian'

from framework import modbase, events, datastreams, wpiwrap, modmaster, moderrors
try:
    import wpilib
except ImportError:
    from pyfrc import wpilib
import time
import json
import logging

class Module(modbase.Module):

    name = "dashboard"

    def module_load(self):
        wpilib.SmartDashboard.init()
        self.joystick1 = datastreams.get_stream("joystick1")
        self.joystick2 = datastreams.get_stream("joystick2")
        self.autonomous_conf_stream = datastreams.get_stream("autonomous_config")
        events.set_callback("run", self.run, self.name)
        wpilib.SmartDashboard.PutNumber("Auto Routine", 2)
        wpilib.SmartDashboard.PutNumber("1st Shoot Distance", 12)
        wpilib.SmartDashboard.PutNumber("2nd Shoot Distance", 7)
        wpilib.SmartDashboard.PutNumber("Distance from Tape", 3)
        wpilib.SmartDashboard.PutNumber("Start Position", 0)



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

            auto_routine = wpilib.SmartDashboard.GetNumber("Auto Routine")
            if auto_routine != last_auto_routine:
                if auto_routine == 0:
                    try:
                        modmaster.get_mod("autonomous").switch_module("modules.christian.auto.dead_auto")
                    except moderrors.ModuleUnloadError:
                        pass

                elif auto_routine == 3:
                    try:
                        modmaster.get_mod("autonomous").switch_module("modules.christian.auto.stupid_auto")
                    except (moderrors.ModuleUnloadError, moderrors.ModuleLoadError) as e:
                        logging.error(e)

                elif auto_routine == 1:
                    try:
                        modmaster.get_mod("autonomous").switch_module("modules.christian.auto.1-ball")
                    except (moderrors.ModuleUnloadError, moderrors.ModuleLoadError) as e:
                        logging.error(e)

                elif auto_routine == 2:
                    try:
                        modmaster.get_mod("autonomous").switch_module("modules.christian.auto.2-ball")
                    except (moderrors.ModuleUnloadError, moderrors.ModuleLoadError) as e:
                        logging.error(e)

                last_auto_routine = auto_routine

                first_shot = wpilib.SmartDashboard.GetNumber("1st Shoot Distance")
                second_shot = wpilib.SmartDashboard.GetNumber("2nd Shoot Distance")
                distance_from_tape = wpilib.SmartDashboard.GetNumber("Distance from Tape")
                start_position = wpilib.SmartDashboard.GetNumber("Start Position")

                self.autonomous_conf_stream.push({"first_shot": first_shot, "second_shot": second_shot, "distance_from_tape": distance_from_tape, "start_position": start_position}, self.name, autolock=True)



            time.sleep(.5)


