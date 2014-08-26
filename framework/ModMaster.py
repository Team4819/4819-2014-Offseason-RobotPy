from framework import ModWrapper

__author__ = 'christian'
import time
import threading
import logging
mods = dict()
eventCallbacks = dict()
modDataStreams = dict()

class moduleLoadError(Exception):
    def __init__(self, name, message):
        logging.error("Module Load Error: " + name + ": " + message)

class moduleUnloadError(Exception):
    def __init__(self, name, message):
        logging.error("Module Unload Error: " + name + ": " + message)


class eventCallback:
    def __init__(self, mod, func, srcmod):
        self.mod = mod
        self.func = func
        self.srcmod = srcmod

    def call(self):
        target = getMod(self.mod).__getattribute__(self.func)
        print(self.mod + "," + self.func )
        thread = threading.Thread(target=target)
        thread.start()

class DataStream(object):
    def __init__(self, defValue):
        self.data = defValue


def getDataStream(streamName, defValue, srcmod="global"):
    if modDataStreams.setdefault(srcmod) is None:
        modDataStreams[srcmod] = dict()
    if modDataStreams[srcmod].setdefault(streamName) is None:
        modDataStreams[srcmod][streamName] = DataStream(defValue)
    return modDataStreams[srcmod][streamName]

def pushToDataStream(streamName, data, srcmod="global"):
    if modDataStreams.setdefault(srcmod) is not None:
        if modDataStreams[srcmod].setdefault(streamName) is not None:
            modDataStreams[srcmod][streamName].data = data

def setEventCallback(event, mod, func, srcmod=None):
    if eventCallbacks.setdefault(event) is None:
        eventCallbacks[event] = list()
    eventCallbacks[event].append(eventCallback(mod, func, srcmod))

def triggerEvent(eventname, srcmod):
    if eventCallbacks.setdefault(eventname) is not None:
        for callback in eventCallbacks[eventname]:
            if callback.srcmod is None or srcmod is callback.srcmod:
                callback.call()
        print("Triggered event " + eventname + " from mod " + srcmod)

def getMod(modname):
    return mods[modname].module

def loadMod(pymodname):
    modwrap = ModWrapper.modWrapper(pymodname)
    modname = modwrap.module.name
    if mods.setdefault(modname) is not None:
        raise moduleLoadError(pymodname, ": Already module with name " + modname)
    mods[modname] = modwrap
    mods[modname].moduleLoad()

def unloadMod(modname):
    if mods.setdefault(modname) is None:
        raise moduleUnloadError(modname, "No such module loaded")
    mods[modname].moduleUnload().wait()


def killAllMods():
    for key in mods:
        mods[key].moduleUnload()

def setAutoReload(setting):
    for key in mods:
        mods[key].autoReload = setting

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
        killAllMods()

    def delayDeath(self):
        self.timer = 0

