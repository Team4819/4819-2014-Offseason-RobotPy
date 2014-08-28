from framework import configerator, moderrors
import logging
import threading
__author__ = 'christian'



class ModWrapper:

    autoReload = False
    modindex = 0
    modlist = list()

    def module_unload(self):
        self.module.module_unload()

    def start(self):
        self.module.start()

    def module_load(self, modname):
        if configerator.parsed_config.setdefault(modname) is None:
            self.pymodule_load(modname)
        else:
            self.modlist = configerator.parsed_config[modname]
            self.load_next_module(modname)

    def pymodule_load(self, pymodname):
        self.pymodname = pymodname
        print("loading module " + pymodname)

        try:
            self.pymod = __import__(pymodname, fromlist=[''])
        except ImportError as e:
            raise moderrors.ModuleLoadError(pymodname, str(e))

        try:
            self.module = self.pymod.Module()
        except AttributeError as e:
            raise moderrors.ModuleLoadError(pymodname, str(e))

        self.module.module_load()
        self.modname = self.module.name

    def switch_module(self):
        self.module_unload()
        self.modindex += 1
        self.load_next_module(self.name)

    def load_next_module(self, subsystem):
            success = False
            while not success:
                if self.modindex == len(self.modlist):
                    raise moderrors.ModuleLoadError(subsystem, "Cannot Load Module: no modules left to try and load for subsystem")
                try:
                    print("Attempting to load module " + self.modlist[self.modindex])
                    self.pymodule_load(self.modlist[self.modindex])
                    threading.Thread(target=self.module.start).start()
                    success = True
                except Exception as e:
                    logging.error(e)
                    self.modindex += 1

    def reload(self):
        self.pymod.reload()
        self.module.__class__ = self.pymod.mod

    def call_wrap(self, func):
        success = False
        while not success:
            try:
                getattr(self.module, func)()
                success = True
            except Exception as e:
                logging.error(e)
                try:
                    self.switch_module()
                except moderrors.ModuleLoadError:
                    return

    def __getattr__(self, item):
        return getattr(self.module, item)








