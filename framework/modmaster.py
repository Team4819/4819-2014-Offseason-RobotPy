__author__ = 'christian'
import time
import threading
import logging
import traceback
import os

from framework import modwrapper, configerator, events
from framework.moderrors import ModuleLoadError, ModuleUnloadError


mods = dict()


ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logging.root.addHandler(ch)


def list_modules():
    module_list = [x for x in mods]
    if "placeholder" in module_list:
        module_list.remove("placeholder")
    return module_list


def load_startup_mods(config=os.path.join("modules", "mods.conf")):
    try:
        modlist = configerator.parse_config(config)["StartupMods"]
    except Exception as e:
        logging.error(e)
        modlist = configerator.parse_config(os.path.join("framework", "defaults", "mods.conf"))["StartupMods"]
    for mod in modlist:
        try:
            load_mod(mod)
        except ModuleLoadError as e:
            logging.error(e)
    events.set_event("run", "modmaster", True)


def get_mod(modname):
    if modname in mods:
        return mods[modname]
    else:
        if "placeholder" not in mods:
            load_mod("framework.dummy_module")
        mods["placeholder"].module.target = modname
        return mods["placeholder"]


def load_mod(pymodname):
    modwrap = modwrapper.ModWrapper()
    modwrap.module_load(pymodname)
    modname = modwrap.modname
    if modname in mods:
        raise ModuleLoadError(modname, ": Already module with name " + modname)
    mods[modname] = modwrap


def unload_mod(modname):
    if modname not in mods:
        raise ModuleUnloadError(modname, "No such module loaded")
    mods[modname].module_unload()
    mods.pop(modname, None)


def kill_all_mods():
    keys = list()
    keys += list_modules()
    for key in keys:
        unload_mod(key)


def reload_mods():
    for key in mods:
        try:
            mods[key].reload()
        except Exception as e:
            logging.error("Error reloading module: " + key + ": " + str(e) + "\n" + traceback.format_exc())


#   This is my solution to the threads that would not die!
class GrimReaper(threading.Thread):
    timer = 0

    def __init__(self):
        super().__init__()

    def run(self):
        while self.timer < 4:
            self.timer += 1
            if self.timer > 2:
                logging.info("The Reaper is coming!")
            time.sleep(.1)
        logging.info("KILL ALL THE THREADS!!!!!")
        kill_all_mods()

    def delay_death(self):
        self.timer = 0

