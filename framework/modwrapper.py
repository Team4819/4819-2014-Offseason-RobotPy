from framework import configerator, moderrors, events
import logging
import threading
import importlib
import traceback
__author__ = 'christian'


class ModWrapper:

    autoReload = False
    modindex = 0
    modlist = list()
    pymodname = "not a module!!"

    def switch_module(self, retry_current=False):
        self.module_unload()
        if not retry_current:
            self.modindex += 1
        self.load_next_module(self.name)
        events.trigger(self.modname + ".load", self.modname + ".ModWrapper")
        events.trigger("run", self.modname + ".ModWrapper", target=self.modname)

    def module_load(self, modname):
        if configerator.parsed_config.setdefault(modname) is None:
            self.pymodule_load(modname)
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
                    logging.error("Error loading module " + self.modlist[self.modindex] + ": " + e)
                    self.modindex += 1

    def pymodule_load(self, pymodname):
        print("loading module " + pymodname)
        #Load Python file, use reload if it is just being reloaded!
        try:
            if pymodname is not self.pymodname:
                self.pymod = __import__(pymodname, fromlist=[''])
            else:
                importlib.reload(self.pymod)
        except ImportError as e:
            raise moderrors.ModuleLoadError(pymodname, str(e))

        try:
            self.module = self.pymod.Module()
        except AttributeError as e:
            raise moderrors.ModuleLoadError(pymodname, str(e))

        self.module.module_load()
        self.modname = self.module.name
        self.pymodname = pymodname

    def reload(self):
        self.switch_module(retry_current=True)

    def async(self, func):
        threading.Thread(target=self.call_wrap, args={func}).start()

    def call_wrap(self, func):
        success = False
        while not success:
            try:
                getattr(self.module, func)()
                success = True
            except Exception as e:
                logging.error("Exception calling func " + func + ": " + str(e) + "\n" + traceback.format_exc())
                try:
                    self.switch_module()
                except moderrors.ModuleLoadError as ex:
                    logging.error(ex)
                    return

    def __getattr__(self, item):
        return getattr(self.module, item)








