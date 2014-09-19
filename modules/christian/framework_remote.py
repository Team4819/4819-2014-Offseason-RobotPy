__author__ = 'christian'

from framework import modbase, events, modmaster
import logging
import time
import json

try:
    import wpilib
except ImportError:
    from pyfrc import wpilib

class Module(modbase.Module):
    name = "remote"
    index = 1

    def module_load(self):
        events.set_callback("run", self.run, self.name)
        wpilib.SmartDashboard.init()
        wpilib.SmartDashboard.PutString("frameworkcommands", "{}")

    def run(self):
        while not self.stop_flag:
            modnames = modmaster.list_modules()
            modsummary = list()
            for name in modnames:
                mod = modmaster.get_mod(name)
                modsummary.append({"name": mod.name, "filename": mod.filename, "runningTasks": mod.runningEvents})
            wpilib.SmartDashboard.PutString("modulesummary", json.dumps(modsummary))

            commandsString = wpilib.SmartDashboard.GetString("frameworkcommands")
            if not commandsString == "{}":
                commands = json.loads(commandsString)
                for command in commands:
                    if int(command) >= self.index:
                        if commands[command]["command"] == "reload module":
                            modmaster.get_mod(commands[command]["target"]).reload()
                        elif commands[command]["command"] == "unload module":
                            modmaster.unload_mod(commands[command]["target"])
                        elif commands[command]["command"] == "load module":
                            modmaster.load_mod(commands[command]["target"])
                        else:
                            logging.error("Framework Remote: No such command - " + commands[command]["command"])
                        self.index = int(command) + 1


            time.sleep(1)