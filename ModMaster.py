__author__ = 'christian'
import logging
import ModWrapper

mods = dict()

def getMod(modname):
    return mods.module

def loadMod(pymodname):
    modwrap = ModWrapper.modWrapper(pymodname)
    modname = modwrap.module.name
    if mods.setdefault(pymodname) is not None:
        raise ModWrapper.moduleError("Already module with name " + modname)
    mods[modname] = modwrap
    mods[modname].start()

def killAllMods():
    for mod in mods:
        mod.stop()



