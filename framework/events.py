import framework.modmaster
__author__ = 'christian'

event_callbacks = dict()
stated_events = list()


class EventCallback:
    def __init__(self, mod, func, srcmod):
        self.mod = mod
        self.func = func
        self.srcmod = srcmod

    def call(self):
        framework.modmaster.get_mod(self.mod).async(self.func)


def remove_callbacks(mod):
    for key in event_callbacks:
        for callback in event_callbacks[key]:
            if callback.mod is mod:
                event_callbacks[key].remove(callback)


def set_callback(event, mod, func, srcmod=None):
    if event not in event_callbacks:
        event_callbacks[event] = list()
    event_callbacks[event].append(EventCallback(mod, func, srcmod))


def set_event(eventname, srcmod, state):
    if eventname not in stated_events and state:
        stated_events.append(eventname)
        trigger(eventname, srcmod)
    elif eventname in stated_events and not state:
        stated_events.remove(eventname)


def refresh_events(target):
    for event in stated_events:
        if event in event_callbacks:
            for callback in event_callbacks[event]:
                if callback.mod is target:
                    callback.call()
    print("Refreshed event " + target)


def trigger(eventname, srcmod, target="all"):
    if eventname in event_callbacks:
        for callback in event_callbacks[eventname]:
            if callback.srcmod is None or srcmod is callback.srcmod:
                if target is "all" or callback.mod is target:
                    callback.call()
        print("Triggered event " + eventname + " from mod " + srcmod)