from framework import configerator, moderrors, events, wpiwrap
import logging
import threading
import imp
import os
import traceback
import time
__author__ = 'christian'


class ModWrapper:

    def __init__(self):
        self.running_events = dict()
        """A list of currently running tasks"""

        self.next_pid = 0
        """The next available process id"""

        self.fallback_list = list()
        """The list of fallback modules to use on case of failure"""

        self.fallback_index = 0
        """The current modules index on the fallback list"""

        self.filename = ""
        """The loaded modules filename"""

        self.subsystem = ""
        """The loaded modules subsystem name"""

        self.mod_loaded = False
        """Is a module currently loaded?"""

        self.module = False
        """The module object"""

        self.modfile = None
        """The imported module file"""

    def replace_faulty(self):
        """Replace a faulty module with the next in line, aka increment fallback_index and trigger load()"""
        self.fallback_index += 1
        self.load()

    def load(self, modname=None):
        """Load a module into the modwrapper, either from a name, or use the existing fallback_list and fallback_index"""

        #Start by unloading any previously loaded module
        if self.mod_loaded:
            self.module_unload()

        #Setup module fallback lists

        #If a module was actually specified
        if modname is not None:

            #is it a subsystem name?
            if modname in configerator.parsed_config:
                self.fallback_list = configerator.parsed_config[modname]
                self.fallback_index = 0

            #no? must be a filename then.
            else:
                #Search for filename in loaded config
                for subsystem_config in configerator.parsed_config:
                    if subsystem_config is not "StartupMods" and modname in configerator.parsed_config[subsystem_config]:
                        #We found it! set the fallback list and module index
                        self.fallback_list = configerator.parsed_config[subsystem_config]
                        self.fallback_index = self.fallback_list.index(modname)

                #If we still don't have a fallback list, just make one up and go!
                if len(self.fallback_list) is 0:
                    self.fallback_list.append(modname)
                    self.fallback_index = 0

        #Now that we have the fallback list, we can loop through it and try to find a module that will successfully load!

        success = False
        while not success:
            #Do we have any more to try?
            if self.fallback_index >= len(self.fallback_list):
                raise moderrors.ModuleLoadError(self.subsystem, "No files left to try and load in the fallback list")

            #Lets try this module, the one selected by modindex
            file_to_load = self.fallback_list[self.fallback_index]
            try:

                logging.info("Loading " + file_to_load)

                if file_to_load == self.filename:
                    #This is the same file we have already loaded! just wipe the cache, if necessary, and reload it!
                    path = getattr(self.modfile, "__cached__")
                    if os.path.exists(path):
                        os.remove(path)
                    self.modfile = imp.reload(self.modfile)
                else:
                    #Load the python file from scratch
                    self.modfile = __import__(file_to_load, fromlist=[''])

                #Get the actual module object, and let the wrapper know that we have the object successfully loaded
                self.module = self.modfile.Module()
                self.mod_loaded = True

                #Trigger the module load function and get the module's true subsystem and file name
                self.module.module_load()
                self.subsystem = self.module.subsystem
                self.filename = file_to_load

                #Trigger a *subsystem*.load event for the rest of the system to hear, and get our newly-loaded module
                #up-to-date on current events
                events.set_event(self.subsystem + ".load", self.subsystem, True)
                events.refresh_events(self.subsystem)

                #Yay, we must have been successfull!
                success = True
            except Exception as e:
                #Oops, something happened. We must try the next one on the fallback list!
                logging.error("Error loading module: " + file_to_load + ": " + str(e) + "\n" + traceback.format_exc())
                if self.mod_loaded:
                    self.module_unload()
                self.fallback_index += 1

    def module_unload(self):
        """Unload the currently loaded module"""

        #If we actually have a module loaded, run it's unload function
        if self.mod_loaded:
            try:
                self.module.module_unload()
            except Exception as e:
                logging.error("Error unloading module: " + self.filename + ": " + str(e) + "\n" + traceback.format_exc())

        #Cleanup all traces of the old module

        #Remove all event callbacks
        events.remove_callbacks(self.subsystem)

        #Let the rest of the system know that this module has been unloaded;
        #stop the *subsystem*.load event and trigger the *subsystem*.unload event
        events.set_event(self.subsystem + ".load", self.subsystem, False)
        events.trigger(self.subsystem + ".unload", self.subsystem)

        #Clear the wpilib references, neuteralizing any outputs
        wpiwrap.clear_refrences(self.subsystem)

        self.mod_loaded = False
        logging.info("unloaded module " + self.subsystem)

    def call_wrap(self, func):
        """This function is responsible for running a module's function in a contained environment and handling any issues"""

        #Grab a process id and increment the reference.
        id = self.next_pid
        self.next_pid += 1

        #Save a running_event with the function's name and start time
        self.running_events[id] = {"name": func.__name__, "starttime": time.time()}

        try:
            #Run the function!
            func()
        except Exception as e:
            #Something happened! Report an exception and try to replace_faulty
            logging.error("Exception calling func " + func.__name__ + ": " + str(e) + "\n" + traceback.format_exc())
            try:
                self.replace_faulty()
            except moderrors.ModuleLoadError as ex:
                #I guess that did not work either, well better report it also.
                logging.error(ex)

        #Clear the processe's entry in running_events
        del(self.running_events[id])

    def __getattr__(self, item):
        #Prevent a feedback loop
        if item == "module":
            raise AttributeError(item)
        #Get that attribute!
        return getattr(self.module, item)








