"""
This is as it's name describes, the core engine for the module system. It contains both top-level functions to
manipulate the module system, as well as the various classes necessary to perform those actions.
"""
__author__ = 'christian'
from framework import configerator, events, wpiwrap
import time
import threading
import logging
import traceback
import os
import imp

mods = dict()
"""The dictionary of all loaded modules, with the module's subsystem as it's key."""

#Initialize console logs
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logging.root.addHandler(ch)


def list_modules():
    """Returns a copy of the list of all loaded mods"""
    return [x for x in mods]


def load_startup_mods(config=os.path.join("modules", "mods.conf")):
    """Load all modules listed in the [StartupMods] tag in a config file"""
    try:
        #Try to get the config file parsed
        startup_mods = configerator.parse_config(config)["StartupMods"]
    except Exception as e:
        #Oops, ERROR! ERROR!
        logging.error(e)
        #Well, try the backup config file then
        startup_mods = configerator.parse_config(os.path.join("framework", "defaults", "mods.conf"))["StartupMods"]

    #For each module in the config, try to load it.
    for mod in startup_mods:
        try:
            load_module(mod)
        except ModuleLoadError as e:
            #If we get an error, report it!
            logging.error(e)


def get_modules(subsystem):
    """Return the wanted module"""
    if subsystem in mods:
        #We have it? Then return it!
        return mods[subsystem]
    else:
        #404 no module found, return the elusive Phantom Object!
        return PhantomObject([subsystem])


def load_module(name):
    """Load a module"""
    #Check to make sure we do not already have one by that name
    if name in mods:
        raise ModuleLoadError(name, ": Already module with name " + name)

    #Create the ModWrapper object and load the module
    modwrap = ModWrapper()
    modwrap.load(name)
    modname = modwrap.subsystem

    #Check again, do we have a duplicate now?
    if modname in mods:
        #Oops, lets clean up this mess we have made
        modwrap.unload()
        raise ModuleLoadError(modname, ": Already module with name " + modname)

    #Save it!
    mods[modname] = modwrap


def unload_module(subsystem):
    """Unload a module by subsystem"""
    if subsystem not in mods:
        raise ModuleUnloadError(subsystem, "No such module loaded")
    #Unload it
    mods[subsystem].unload()
    #Delete it
    mods.pop(subsystem, None)


def kill_all_modules():
    """KILL ALL THE MODULES"""
    modules = list_modules()
    for mod in modules:
        unload_module(mod)


def reload_mods():
    """Reload all modules"""
    for key in mods:
        try:
            mods[key].reload()
        except Exception as e:
            logging.error("Error reloading module: " + key + ": " + str(e) + "\n" + traceback.format_exc())


#   This is my solution to the threads that would not die!
class GrimReaper(threading.Thread):
    """This watches for the status of the main thread, and kills the modules when the main thread dies."""

    timer = 0
    #How many seconds have elapsed since last we heard from the main thread

    def run(self):
        while self.timer < 2:
            #Increment the timer each iteration
            self.timer += .1
            #If we have less than 1 second left,
            if self.timer > 1:
                #Give a warning
                logging.info("The Reaper is coming!")
            time.sleep(.1)
        #Notify the system and kill all modules
        logging.info("KILL ALL THE THREADS!!!!!")
        kill_all_modules()

    def delay_death(self):
        """Reset the death timer"""
        self.timer = 0


class ModWrapper:
    """This is the final layer managing a module,"""

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
            self.unload()

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
                raise ModuleLoadError(self.subsystem, "No files left to try and load in the fallback list")

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
                    self.unload()
                self.fallback_index += 1

    def unload(self):
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
            except ModuleLoadError as ex:
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


class ModuleLoadError(Exception):
    """This error is for errors during module load"""
    def __init__(self, name, message):
        super().__init__(name + ": " + message)


class ModuleUnloadError(Exception):
    """This error is for errors during module unload"""
    def __init__(self, name, message):
        super().__init__(name + ": " + message)


class PhantomObject():
    """This is what is returned when a non-existant module is asked for"""

    chain = list()
    """The chain of objects called to get to the called function."""

    def __init__(self, chain=list()):
        self.chain = chain

    def __getattr__(self, item):
        #If an attribute is wanted, return another PhantomObject, appending the currently requested attribute name
        self.chain.append(item)
        return PhantomObject(self.chain)

    def __call__(self, *args, **kwargs):
        #The attribute was called, so print a warning with the chain of phantom attributes
        function_name = self.chain[len(self.chain) - 1]
        text = "Phantom object reports phantom call! Called " + function_name + ", chain:"
        for link in self.chain:
            text += "Phantom object " + link + ",\n"
        logging.warning(text)


class ModuleBase(object):
    """The parent class for all modules"""
    subsystem = "generic"
    stop_flag = False

    def module_load(self):
        """The module's constructor, initialize all references and interfaces here"""
        pass

    def module_unload(self):
        """The module's destructor, stop any loops and do any clean-up here."""
        self.stop_flag = True