__author__ = 'christian'
import ModWrapper
import time
import threading
mods = dict()
events = dict()
eventCallbacks = dict()

def getEvent(eventname):
    event = threading.Event()
    if events.setdefault(eventname) is None:
        events[eventname] = list()
    events[eventname].append(event)
    return event

def onEvent(eventname, func):
    if eventCallbacks.setdefault(eventname) is None:
        eventCallbacks[eventname] = list()
    eventCallbacks[eventname].append(func)

def setEvent(eventname):
    if events.setdefault(eventname) is None and eventCallbacks.setdefault(eventname) is None:
        print("Warning: No events registered for event " + eventname)
        return
    if events.setdefault(eventname) is not None:
        for event in events[eventname]:
            event.set()
    if eventCallbacks.setdefault(eventname) is not None:
        for callback in eventCallbacks[eventname]:
            callback()
    print("Triggered event " + eventname)

def getMod(modname):
    return mods[modname].module

def loadMod(pymodname):
    modwrap = ModWrapper.modWrapper(pymodname)
    modname = modwrap.module.name
    if mods.setdefault(modname) is not None:
        raise ModWrapper.moduleError("Already module with name " + modname)
    mods[modname] = modwrap
    mods[modname].moduleLoad()

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



