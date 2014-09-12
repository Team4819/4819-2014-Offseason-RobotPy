import logging
import threading
import framework.modmaster
from framework.record import recorder

__author__ = 'christian'

event_callbacks = dict()
stated_events = list()


class EventCallback:
    def __init__(self, callback, tgtmod, srcmod):
        self.func = callback
        self.srcmod = srcmod
        self.tgtmod = tgtmod

    def call(self):
        threading.Thread(target=framework.modmaster.get_mod(self.tgtmod).call_wrap, args={self.func}).start()


def remove_callbacks(mod):
    for key in event_callbacks:
        for callback in event_callbacks[key]:
            if callback.tgtmod is mod:
                event_callbacks[key].remove(callback)


def set_callback(event, callback, tgtmod=None, srcmod=None):
    if event not in event_callbacks:
        event_callbacks[event] = list()
    event_callbacks[event].append(EventCallback(callback, tgtmod, srcmod))


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
                if callback.tgtmod is target:
                    try:
                        callback.call()
                    except Exception as e:
                        logging.error(e)
    logging.info("Refreshed event " + target)


def trigger(eventname, srcmod, action="triggered"):
    recorder.log_event(action, eventname, srcmod)
    if eventname in event_callbacks:
        for callback in event_callbacks[eventname]:
            if callback.srcmod is None or srcmod == callback.srcmod:
                try:
                    callback.call()
                except Exception as e:
                    logging.error(e)
        logging.info("Triggered event " + eventname + " from mod " + srcmod)


def purge_events():
    global stated_events, event_callbacks
    keys = list()
    keys += event_callbacks.keys()
    for key in keys:
        del(event_callbacks[key])
    stated_events = list()