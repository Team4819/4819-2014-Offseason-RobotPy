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
    """
    This module interfaces with the python application under scripts/remote.py.
    It publishes data over Network Tables and obeys commands sent back to it.
    """
    subsystem = "remote"
    #The last-used command index
    command_index = 1

    def __init__(self):
        #Initialize Network Tables
        wpilib.SmartDashboard.init()
        self.table = wpilib.NetworkTable.GetTable("framework_remote")
        self.table.PutString("frameworkcommands", "{}")

        #Setup callback
        events.add_callback("run", self.subsystem, self.run)

    def run(self, task):
        while task.active:
            #Get a list of all modules and send it to the table
            modnames = module_engine.list_modules()
            self.table.PutString("modlist", json.dumps(modnames))

            #Loop through all loaded modules and get some info about them,
            #  then publish it to the table as a json string.
            for name in modnames:
                mod = module_engine.get_modules(name)
                modsummary = {"name": mod.subsystem, "filename": mod.filename, "runningTasks": mod.running_events, "fallbackList": mod.fallback_list}
                self.table.PutString("mod." + name, json.dumps(modsummary))

            #Try to update our command_index if there is a larger remote one.
            # this is to ensure that we do not run the same command again if we restart.
            try:
                remoteindex = self.table.GetNumber("globalCommandIndex")
                if self.command_index < remoteindex:
                    self.command_index = remoteindex
            except wpilib.TableKeyNotDefinedException:
                pass

            #Get the commands data from the table and parse it if there is anything to parse.
            commandsString = self.table.GetString("frameworkcommands")
            if not commandsString == "{}":
                commands = json.loads(commandsString)

                #For each command, check if it is greater than our command_index, and if so, do it!
                for command in commands:
                    if int(command) >= self.command_index:
                        self.command_index = int(command) + 1

                        #Update the global command index
                        self.table.PutNumber("globalCommandIndex", self.command_index)

                        #Find and run the command
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
                            #Oops, my bad. :L
                            logging.error("Error running command: " + commands[command]["command"] + ": " + str(e) + "\n" + traceback.format_exc())

            time.sleep(.5)