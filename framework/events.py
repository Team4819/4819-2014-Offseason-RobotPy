import logging
import framework.modmaster
from framework.record import recorder

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
        trigger(eventname, srcmod, action="on")
    elif eventname in stated_events and not state:
        stated_events.remove(eventname)
        recorder.log_event("off", eventname, srcmod)

def refresh_events(target):
    for event in stated_events:
        if event in event_callbacks:
            for callback in event_callbacks[event]:
                if callback.mod is target:
                    callback.call()
    logging.info("Refreshed event " + target)


def trigger(eventname, srcmod, action="triggered"):
    recorder.log_event(action, eventname, srcmod)
    if eventname in event_callbacks:
        for callback in event_callbacks[eventname]:
            if callback.srcmod is None or srcmod == callback.srcmod:
                callback.call()
        logging.info("Triggered event " + eventname + " from mod " + srcmod)


def purge_events():
    global stated_events, event_callbacks
    keys = list()
    keys += event_callbacks.keys()
    for key in keys:
        del(event_callbacks[key])
    stated_events = list()