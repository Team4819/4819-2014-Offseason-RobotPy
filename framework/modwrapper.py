from framework import configerator, moderrors
import logging
__author__ = 'christian'



class ModWrapper:

    autoReload = False
    modindex = 0
    modlist = list()

    def module_unload(self):
        pass

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
        self.load_next_module(self.name)

    def load_next_module(self, subsystem):
            success = False
            while not success:
                if self.modindex == len(self.modlist):
                    raise moderrors.ModuleLoadError("Cannot Load Module: no modules left to try and load for subsystem " + subsystem)
                try:
                    print("Attempting to load module " + self.modlist[self.modindex])
                    self.pymodule_load(self.modlist[self.modindex])
                    success = True
                except moderrors.ModuleLoadError:
                    self.modindex += 1

    def kill(self):
        self.module.stop()

    def reload(self):
        self.pymod.reload()
        self.module.__class__ = self.pymod.mod

    def __getattr__(self, item):
        attribute = object.__getattribute__(self.module, item)
        if hasattr(attribute, "__call__"):
            return FuncWrapper(item, self)
        else:
            return attribute


class FuncWrapper:
    def __init__(self, item, modwrap):
        self.func = item
        self.modwrap = modwrap

    def __call__(self, *args, **kwargs):
        success = False
        while not success:
            try:
                target = object.__getattribute__(self.modwrap, self.func)
                target(*args, **kwargs)
                success = True
            except Exception as e:
                logging.error(e)
                try:
                    self.modwrap.switch_module()
                except moderrors.ModuleLoadError:
                    return







