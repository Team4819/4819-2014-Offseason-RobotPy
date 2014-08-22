
__author__ = 'christian'
import logging

class moduleError(Exception):
    pass

class modWrapper:

    def __init__(self,pymodname):
        self.pymodname = pymodname
        print("loading module " + pymodname)
        try:
            self.pymod = __import__(pymodname, fromlist=[''])
        except ImportError:
            raise moduleError("Error importing module " + pymodname)
        if hasattr(self.pymod, "module"):
            self.module = self.pymod.module()
        else:
            raise moduleError("No module class in " + pymodname)
        if hasattr(self.pymod, "name"):
            self.modname = self.pymod.name

    def start(self):
        logging.info("Starting Module " + self.pymodname)
        if hasattr(self.module, "start"):
            self.module.start()
            print("Module " + self.pymodname + "Started")
        else:
            print("No start Method Found in module " + self.pymodname)

    def kill(self):
        self.module.stop();

    def __getattr__(self, item):
        if super.__getattr__(self, item) is None:
            return self.module.__getattr__(item)
        else:
            return super.getattr__(self, item)



