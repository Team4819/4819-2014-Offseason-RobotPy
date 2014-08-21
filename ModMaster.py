__author__ = 'christian'
import logging
import ModWrapper

mods = dict()

def getMod(modname):
    return mods.module

def loadMod(pymodname):
    modwrap = ModWrapper.modWrapper(pymodname)
    modname = modwrap.module.name
    mods[modname] = modwrap
    mods[modname].start()