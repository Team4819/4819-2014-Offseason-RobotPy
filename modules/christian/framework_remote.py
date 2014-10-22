__author__ = 'christian'
from framework import events, module_engine
import logging
import traceback
import time
import json

try:
    import wpilib
except ImportError:
    from pyfrc import wpilib

#import pynetworktables as wpilib


class Module:
    subsystem = "remote"
    stop_flag = False
    index = 1

    def __init__(self):
        events.add_callback("run", self.subsystem, callback=self.run, inverse_callback=self.stop)
        wpilib.SmartDashboard.init()
        self.table = wpilib.NetworkTable.GetTable("framework_remote")
        self.table.PutString("frameworkcommands", "{}")

    def run(self):
        self.stop_flag = False
        while not self.stop_flag:
            modnames = module_engine.list_modules()
            self.table.PutString("modlist", json.dumps(modnames))
            for name in modnames:
                mod = module_engine.get_modules(name)
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
                        self.table.PutNumber("globalCommandIndex", self.index)
                        try:
                            if commands[command]["command"] == "reload module":
                                module_engine.get_modules(commands[command]["target"]).load()
                            elif commands[command]["command"] == "unload module":
                                module_engine.unload_module(commands[command]["target"])
                            elif commands[command]["command"] == "load module":
                                module_engine.load_module(commands[command]["target"])
                            else:
                                logging.error("Framework Remote: No such command - " + commands[command]["command"])
                        except Exception as e:
                            logging.error("Error running command: " + commands[command]["command"] + ": " + str(e) + "\n" + traceback.format_exc())

            time.sleep(.5)

    def stop(self):
        self.stop_flag = True