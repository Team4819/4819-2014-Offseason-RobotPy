import framework.modmaster
__author__ = 'christian'

event_callbacks = dict()


class EventCallback:
    def __init__(self, mod, func, srcmod):
        self.mod = mod
        self.func = func
        self.srcmod = srcmod

    def call(self):
        framework.modmaster.get_mod(self.mod).async(self.func)


def set_callback(event, mod, func, srcmod=None):
    if event_callbacks.setdefault(event) is None:
        event_callbacks[event] = list()
    event_callbacks[event].append(EventCallback(mod, func, srcmod))


def trigger(eventname, srcmod, target="all"):
    if event_callbacks.setdefault(eventname) is not None:
        for callback in event_callbacks[eventname]:
            if callback.srcmod is None or srcmod is callback.srcmod:
                if target is "all" or callback.mod is target:
                    callback.call()
        print("Triggered event " + eventname + " from mod " + srcmod)