"""
This is as it's name describes, the core engine for the module system. It contains both top-level functions to
manipulate the module system, as well as the various classes necessary to perform those actions.
"""

__author__ = 'christian'
from framework import events, wpiwrap, filesystem
import time
import threading
import logging
import traceback
import os
import imp

_loaded_modules = dict()
"""The dictionary of all loaded modules, with the module's subsystem as it's key."""

#Initialize console logs
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logging.root.addHandler(ch)


def list_modules():
    """Returns a copy of the list of all loaded mods"""
    return [x for x in _loaded_modules]


def load_startup_mods(config=os.path.join("modules", "mods.conf")):
    """Load all modules listed in the [StartupMods] tag in a config file"""
    try:
        #Try to get the config file parsed
        startup_mods = filesystem.parse_config(config)["StartupMods"]
    except Exception as e:
        #Oops, ERROR! ERROR!
        logging.error(e)
        #Well, try the backup config file then
        startup_mods = filesystem.parse_config(os.path.join("framework", "defaults", "mods.conf"))["StartupMods"]

    #For each module in the config, try to load it.
    for mod in startup_mods:
        try:
            load_module(mod)
        except ModuleLoadError as e:
            #If we get an error, report it!
            logging.error(e)


def get_modules(subsystem):
    """Return the wanted module"""
    if subsystem in _loaded_modules:
        #We have it? Then return it!
        return _loaded_modules[subsystem]
    else:
        #404 no module found, return a Phantom Object.
        return PhantomObject([subsystem])


def load_module(name):
    """Load a module"""
    #Check to make sure we do not already have one by that name
    if name in _loaded_modules:
        raise ModuleLoadError(name, ": Already module with name " + name)

    #Create the _ModWrapper object and load the module
    modwrap = _ModWrapper()
    modwrap.load(name)
    subsystem = modwrap.subsystem

    #Check again, do we have a duplicate now?
    if subsystem in _loaded_modules:
        #Oops, lets clean up this mess we have made
        modwrap.unload()
        raise ModuleLoadError(subsystem, ": Already module with name " + subsystem)

    #Save it!
    _loaded_modules[subsystem] = modwrap

    #Trigger a *subsystem*.load event for the rest of the system to hear, and get our newly-loaded module
    #up-to-date on current events
    events.start_event(subsystem + ".load", subsystem)
    events.repeat_callbacks(subsystem)


def unload_module(subsystem):
    """Unload a module by subsystem"""
    if subsystem not in _loaded_modules:
        raise ModuleUnloadError(subsystem, "No such module loaded")
    #Unload it
    _loaded_modules[subsystem].unload()
    #Delete it
    _loaded_modules.pop(subsystem, None)


def kill_all_modules():
    """KILL ALL THE MODULES"""
    modules = list_modules()
    for mod in modules:
        unload_module(mod)


def reload_mods():
    """Reload all modules"""
    for key in _loaded_modules:
        try:
            _loaded_modules[key].reload()
        except Exception as e:
            logging.error("Error reloading module: " + key + ": " + str(e) + "\n" + traceback.format_exc())


#   This is my solution to the threads that would not die!
class Janitor(threading.Thread):
    """This watches for the status of the main thread, and kills the modules when the main thread dies."""

    timer = 0
    #How many seconds have elapsed since last we heard from the main thread

    def run(self):
        while self.timer < 2:
            #Increment the timer each iteration
            self.timer += .2
            #If we have less than 1 second left,
            if self.timer > 1:
                #Give a warning
                logging.info("The Janitor is coming!")
            time.sleep(.2)
        #Notify the system and kill all modules
        logging.info("Cleaning up all the modules!!!!!")
        kill_all_modules()

    def delay_death(self):
        """Reset the death timer"""
        self.timer = 0


class _ModWrapper:
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

    def reload(self):
        self.load()

    def load(self, modname=None):
        """
        Load a module into the modwrapper, either from a name, or use the existing fallback_list and fallback_index
        """

        #Start by unloading any previously loaded module
        if self.mod_loaded:
            self.unload()

        #Setup module fallback lists

        #If a module was actually specified
        if modname is not None:

            #is it a subsystem name?
            if modname in filesystem.parsed_config:
                self.fallback_list = filesystem.parsed_config[modname]
                self.fallback_index = 0

            #no? must be a filename then.
            else:
                #Search for filename in loaded config
                for subsystem_config in filesystem.parsed_config:
                    if subsystem_config != "StartupMods" and modname in filesystem.parsed_config[subsystem_config]:
                        #We found it! set the fallback list and module index
                        self.fallback_list = filesystem.parsed_config[subsystem_config]
                        self.fallback_index = self.fallback_list.index(modname)

                #If we still don't have a fallback list, just make one up and go!
                if len(self.fallback_list) is 0:
                    self.fallback_list.append(modname)
                    self.fallback_index = 0

        #Now that we have the fallback list, we can loop through it
        # and try to find a module that will successfully load!

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

                #Get the module's true subsystem and file name
                self.subsystem = self.module.subsystem
                self.filename = file_to_load

                #Check to see if we are already saved in _loaded_modules
                if self.subsystem in _loaded_modules and self is _loaded_modules[self.subsystem]:
                    #Trigger a *subsystem*.load event for the rest of the system to hear, and get our newly-loaded module
                    #up-to-date on current events
                    events.start_event(self.subsystem + ".load", self.subsystem)
                    events.repeat_callbacks(self.subsystem)

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

        #Remove all event callbacks and active events, triggering any inverse events
        events.remove_callbacks(self.subsystem)

        #Let the rest of the system know that this module has been unloaded;
        #stop the *subsystem*.load event and trigger the *subsystem*.unload event
        events.stop_event(self.subsystem + ".load", self.subsystem)
        events.trigger_event(self.subsystem + ".unload", self.subsystem)

        #Clear the wpilib references, neuteralizing any outputs
        wpiwrap.clear_refrences(self.subsystem)

        self.mod_loaded = False
        logging.info("unloaded module " + self.subsystem)

    def call_wrap(self, func, *args, **kwargs):
        """
        This function is responsible for running a module's function in a contained environment
        and handling any issues
        """

        #Grab a process id and increment the reference.
        id = self.next_pid
        self.next_pid += 1

        #Save a running_event with the function's name and start time
        self.running_events[id] = {"name": func.__name__, "starttime": time.time()}

        try:
            #Run the function!
            func(*args, **kwargs)
        except Exception as e:
            #Something happened! Report an exception and try to replace_faulty
            logging.error("Exception calling func " + func.__name__ + ": " + str(e) + "\n" + traceback.format_exc())
            try:
                self.replace_faulty()
            except ModuleLoadError as ex:
                #I guess that did not work either, well better report it also.
                logging.error(ex)

        #Clear the process's entry in running_events
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


class PhantomObject:
    """
    This is what is returned when a non-existent module is asked for.
    It stores a stack of requested (and non-existent) attributes, and logs them
    if the attribute is called.
    """

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
            text += "\n Phantom object " + link + ","
        logging.warning(text)