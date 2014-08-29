import time
import threading
from framework import modwrapper, configerator, events
from framework.moderrors import ModuleLoadError, ModuleUnloadError


__author__ = 'christian'


mods = dict()


def load_startup_mods():
    modlist = configerator.get_config()["StartupMods"]
    for mod in modlist:
        try:
            load_mod(mod)
        except ModuleLoadError:
            pass


def get_mod(modname):
    if modname in mods:
        return mods[modname]
    else:
        if "generic" not in mods:
            load_mod("framework.modbase")
        return mods["generic"]


def load_mod(pymodname):
    modwrap = modwrapper.ModWrapper()
    modwrap.module_load(pymodname)
    modname = modwrap.module.name
    if mods.setdefault(modname) is not None:
        raise ModuleLoadError(modname, ": Already module with name " + modname)
    mods[modname] = modwrap
    events.trigger(modname + ".load", "ModMaster")
    events.trigger("run", "ModMaster", target=modname)


def unload_mod(modname):
    if mods.setdefault(modname) is None:
        raise ModuleUnloadError(modname, "No such module loaded")
    mods[modname].module_unload()


def kill_all_mods():
    for key in mods:
        mods[key].module_unload()


def reload_mods():
    for key in mods:
        mods[key].reload()


def on_modload(target, module, callback):
    events.set_callback(target + ".load", module, callback)
    if module in mods:
        mods[target].async(callback)


#   This is my solution to the threads that would not die!
class GrimReaper(threading.Thread):
    timer = 0

    def __init__(self):
        super().__init__()

    def run(self):
        while self.timer < 4:
            self.timer += 1
            if self.timer > 2:
                print("The Reaper is coming!")
            time.sleep(.1)
        print("KILL ALL THE THREADS!!!!!")
        kill_all_mods()

    def delay_death(self):
        self.timer = 0

