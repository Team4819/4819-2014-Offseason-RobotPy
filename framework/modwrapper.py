from framework import configerator, moderrors, events
import logging
import threading
import imp
import os
import traceback
import time
__author__ = 'christian'


class ModWrapper:

    modindex = 0
    pymodname = ""
    filename = ""


    def __init__(self):
        self.runningEvents = dict()
        self.modlist = list()

    def switch_module(self, retry_current=False):
        self.module_unload()
        if not retry_current:
            self.modindex += 1
        self.load_next_module(self.name)

    def module_load(self, modname):
        if modname not in configerator.parsed_config:
            self.pymodule_load(modname)
            self.modlist.append(self.pymodname)
        else:
            self.modlist = configerator.parsed_config[modname]
            self.load_next_module(modname)

    def load_next_module(self, subsystem):
            success = False
            while not success:
                if self.modindex == len(self.modlist):
                    raise moderrors.ModuleLoadError(subsystem, "Cannot Load Module: no modules left to try and load for subsystem")
                try:
                    self.pymodule_load(self.modlist[self.modindex])
                    success = True
                except Exception as e:
                    logging.error("Error loading module " + self.modlist[self.modindex] + ": " + str(e))
                    self.modindex += 1

    def pymodule_load(self, pymodname):
        logging.info("loading module " + pymodname)
        #Load Python file, use reload if it is just being reloaded!
        try:
            if pymodname is not self.pymodname:
                self.pymod = __import__(pymodname, fromlist=[''])
            else:
                #os.remove(getattr(self.pymod, "__cached__"))
                self.pymod = imp.reload(self.pymod)
        except ImportError as e:
            raise moderrors.ModuleLoadError(pymodname, str(e))

        try:
            self.module = self.pymod.Module()
        except AttributeError as e:
            raise moderrors.ModuleLoadError(pymodname, str(e))

        self.module.module_load()
        self.modname = self.module.name
        self.pymodname = pymodname
        self.filename = pymodname
        events.set_event(self.modname + ".load", self.modname, True)
        events.refresh_events(self.modname)

    def module_unload(self):
        self.module.module_unload()
        events.set_event(self.modname + ".load", self.modname, False)
        events.trigger(self.modname + ".unload", self.modname)
        events.remove_callbacks(self.modname)
        logging.info("unloaded module " + self.modname)

    def reload(self):
        self.switch_module(retry_current=True)

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
                self.switch_module()
            except moderrors.ModuleLoadError as ex:
                logging.error(ex)


    def __getattr__(self, item):
        return getattr(self.module, item)








