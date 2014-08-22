__author__ = 'christian'
import logging
import ModWrapper

mods = dict()



def getMod(modname):
    return mods.module

def loadMod(pymodname):
    modwrap = ModWrapper.modWrapper(pymodname)
    modname = modwrap.module.name
    if mods[modname] is not None:
        raise moduleError("Already module with name " + modname)
    mods[modname] = modwrap
    mods[modname].start()


class moduleError(Exception):
    pass