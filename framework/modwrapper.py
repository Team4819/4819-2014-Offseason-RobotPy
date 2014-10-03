from framework import configerator, moderrors, events, wpiwrap
import logging
import threading
import imp
import os
import traceback
import time
__author__ = 'christian'


class ModWrapper:

    modindex = 0
    filename = ""


    def __init__(self):
        self.runningEvents = dict()
        self.modlist = list()
        self.pymodname = ""
        self.filename = ""
        self.modname = ""

    def switch_module(self, filename):
        self.module_unload()
        self.module_load(filename)


    def cascade_module(self, retry_current=False):
        """Unload the current module and load the next one on the list"""
        self.module_unload()
        if not retry_current:
            self.modindex += 1
        self.load_next_module()

    def module_load(self, modname):
        """Load Module from string, either subsystem or filename"""
        if modname not in configerator.parsed_config:
            config = configerator.parsed_config
            cascade_rules = list()
            cascade_rules.append(modname)
            for section in config:
                if section != "StartupMods" and modname in config[section]:
                    cascade_rules = config[section]
            self.modindex = cascade_rules.index(modname)
            self.modlist = cascade_rules
            self.load_next_module()

        else:
            self.modname = modname
            self.modlist = configerator.parsed_config[modname]
            self.load_next_module()

    def load_next_module(self):
        """Load next module on modlist starting with modindex"""
        success = False
        while not success:
            if self.modindex == len(self.modlist):
                raise moderrors.ModuleLoadError(self.modname, "Cannot Load Module: no modules left to try and load for subsystem")
            try:
                self.pymodule_load(self.modlist[self.modindex])
                success = True
            except Exception as e:
                logging.error("Error loading module: " + self.modlist[self.modindex] + ": " + str(e) + "\n" + traceback.format_exc())
                self.module_unload()
                self.modindex += 1

    def pymodule_load(self, pymodname):
        """Load file straight from pymodname"""
        logging.info("loading module " + pymodname)
        #Load Python file, use reload if it is just being reloaded!
        try:
            if pymodname != self.pymodname:
                self.pymod = __import__(pymodname, fromlist=[''])
            else:
                path = getattr(self.pymod, "__cached__")
                if os.path.exists(path):
                    os.remove(path)
                self.pymod = imp.reload(self.pymod)
        except ImportError as e:
            raise moderrors.ModuleLoadError(pymodname, str(e))

        try:
            self.module = self.pymod.Module()
        except AttributeError as e:
            raise moderrors.ModuleLoadError(pymodname, str(e))

        self.modname = self.module.name
        self.pymodname = pymodname
        self.filename = pymodname


        self.module.module_load()


        events.set_event(self.modname + ".load", self.modname, True)
        events.refresh_events(self.modname)

    def module_unload(self):

        try:
            self.module.module_unload()
        except Exception as e:
            logging.error("Error unloading module: " + self.modlist[self.modindex] + ": " + str(e) + "\n" + traceback.format_exc())

        events.remove_callbacks(self.modname)
        events.set_event(self.modname + ".load", self.modname, False)
        events.trigger(self.modname + ".unload", self.modname)
        wpiwrap.clear_refrences(self.modname)
        logging.info("unloaded module " + self.modname)

    def reload(self):
        self.cascade_module(retry_current=True)

    funcid_current = 0

    def call_wrap(self, func):
        id = self.funcid_current
        self.funcid_current = self.funcid_current + 1
        obj = {"name": func.__name__, "starttime": time.clock()}
        self.runningEvents[id] = obj
        try:
            func()
            del(self.runningEvents[id])
        except Exception as e:
            del(self.runningEvents[id])
            logging.error("Exception calling func " + func.__name__ + ": " + str(e) + "\n" + traceback.format_exc())
            try:
                self.cascade_module()
            except moderrors.ModuleLoadError as ex:
                logging.error(ex)

    def __getattr__(self, item):
        if item == "module":
            raise AttributeError(item)
        return getattr(self.module, item)








