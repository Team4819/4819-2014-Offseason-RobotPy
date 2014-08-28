from framework import configerator, moderrors
__author__ = 'christian'



class ModWrapper:

    autoReload = False

    def module_unload(self):
        pass

    def module_load(self, modname):
        if configerator.parsed_config.setdefault(modname) is None:
            self.pymodule_load(modname)
        else:
            modlist = configerator.parsed_config[modname]
            success = False
            index = 0
            while not success:
                if index == len(modlist):
                    raise moderrors.ModuleLoadError("Cannot Load Module " + modname)
                try:
                    print("Attempting to load module " + modlist[index])
                    self.pymodule_load(modlist[index])
                    success = True
                except moderrors.ModuleLoadError:
                    index += 1

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


    def run(self):
        self.module.run()

    def switch_module(self, pymodname):
        self.module_unload()


    def kill(self):
        self.module.stop()

    def reload(self):
        self.pymod.reload()
        self.module.__class__ = self.pymod.mod


    def __getattr__(self, item):
        return getattr(self.module, item)







