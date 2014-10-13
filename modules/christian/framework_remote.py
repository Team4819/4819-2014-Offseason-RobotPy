__author__ = 'christian'

from framework import modbase, events, modmaster
import logging
import traceback
import time
import json

try:
    import wpilib
except ImportError:
    from pyfrc import wpilib

#import pynetworktables as wpilib

class Module(modbase.Module):
    subsystem = "remote"
    index = 1

    def module_load(self):
        events.set_callback("run", self.run, self.subsystem)
        wpilib.SmartDashboard.init()
        self.table = wpilib.NetworkTable.GetTable("framework_remote")
        self.table.PutString("frameworkcommands", "{}")

    def run(self):
        while not self.stop_flag:
            modnames = modmaster.list_modules()
            self.table.PutString("modlist", json.dumps(modnames))
            for name in modnames:
                mod = modmaster.get_mod(name)
                modsummary = {"name": mod.subsystem, "filename": mod.filename, "runningTasks": mod.running_events, "fallbackList": mod.fallback_list}
                self.table.PutString("mod." + name, json.dumps(modsummary))

            try:
                remoteindex = self.table.GetNumber("globalCommandIndex")
                if self.index < remoteindex:
                    self.index = remoteindex
            except wpilib.TableKeyNotDefinedException:
                pass

            commandsString = self.table.GetString("frameworkcommands")
            if not commandsString == "{}":
                commands = json.loads(commandsString)
                for command in commands:
                    if int(command) >= self.index:
                        self.index = int(command) + 1
                        print(self.index)
                        self.table.PutNumber("globalCommandIndex", self.index)
                        try:
                            if commands[command]["command"] == "reload module":
                                modmaster.get_mod(commands[command]["target"]).load()
                            elif commands[command]["command"] == "unload module":
                                modmaster.unload_mod(commands[command]["target"])
                            elif commands[command]["command"] == "load module":
                                modmaster.load_mod(commands[command]["target"])
                            else:
                                logging.error("Framework Remote: No such command - " + commands[command]["command"])
                        except Exception as e:
                            logging.error("Error running command: " + commands[command]["command"] + ": " + str(e) + "\n" + traceback.format_exc())



            time.sleep(.5)