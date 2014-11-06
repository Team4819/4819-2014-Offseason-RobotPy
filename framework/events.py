"""
This is an event system. Modules can add callbacks to events, which will be run in a new thread once triggered.
This is the primary mechanism for starting and stopping run loops.

On the flip side, events can be either "triggered" which is a one-time call (For example: shoot_cannon or reset_gyro),
 or they can be started and then stopped, for events with duration (For example: run, teleoperated, or enabled).
 The main difference is that when modules are freshly loaded, the refresh_events method is called, which then finds all
 of the "started" events and triggers them for the new module.
"""

import logging
import threading
import framework.module_engine

__author__ = 'christian'

#All event callback objects
_event_callbacks = dict()
#All triggered stated events
_active_events = list()


class _EventCallback:
    """This represents a callback to an event"""

    def __init__(self, callback, tgtmod, inv_func):
        #Set variables
        self.func = callback
        self.inv_func = inv_func
        self.subsystem = tgtmod

    def call(self):
        """Asynchronously call the main callback function"""
        threading.Thread(target=framework.module_engine.get_modules(self.subsystem).call_wrap, args={self.func}).start()

    def call_inverse(self):
        """Asynchronously call the inverse callback function"""
        threading.Thread(target=framework.module_engine.get_modules(self.subsystem).call_wrap, args={self.inv_func}).start()


def add_callback(event, subsystem, callback=lambda: True, inverse_callback=lambda: True):
    """Set a callback for a specified event, callback function, target module, source module, and inverse callback"""
    #If there is no such event already listed, than create the list
    if event not in _event_callbacks:
        _event_callbacks[event] = list()
    #Create the callback object and add it to the list
    _event_callbacks[event].append(_EventCallback(callback, subsystem, inverse_callback))


def start_event(eventname, src_subsystem):
    """Start the event"""
    #If the event is not already started
    if eventname not in [x["event"] for x in _active_events]:
        #Add event to active_events and trigger all callbacks
        _active_events.append({"event": eventname, "src_subsystem": src_subsystem})
        trigger_event(eventname, src_subsystem)


def stop_event(eventname, src_subsystem):
    """Stop the event"""
    #Scan through each active event
    for event in _active_events[:]:
        #If it is the correct event
        if event["event"] is eventname:
            #Clear active_events of event and trigger all inverse callbacks
            _active_events.remove(event)
            trigger_event(eventname, src_subsystem, inverse_event=True)


def trigger_event(eventname, src_subsystem, inverse_event=False):
    """Trigger all callbacks for an event"""
    #If we even have callbacks for this eventname
    if eventname in _event_callbacks:
        #Then go through them all and call them!
        for callback in _event_callbacks[eventname]:
            try:
                #If we want the normal one
                if not inverse_event:
                    callback.call()
                #Otherwise, we want the inverse callback
                else:
                    callback.call_inverse()
            except Exception as e:
                #Naughty Naughty, little callback!
                logging.error("Exception calling callback on event " + eventname + ": " + str(e))
        #Let the system know
        if not inverse_event:
            logging.info("Triggered callbacks for event " + eventname + " by subsystem " + src_subsystem)
        else:
            logging.info("Triggered inverse callbacks for event " + eventname + " by subsystem " + src_subsystem)


def refresh_events(subsystem):
    """Check if subsystem has callbacks for anything in active_events, and call them if so"""
    #For each active event
    for event in _active_events:
        #If we have any callbacks for it
        if event["event"] in _event_callbacks:
            #Check each one to see if it points to the subsystem
            for callback in _event_callbacks[event["event"]]:
                if callback.subsystem is subsystem:
                    try:
                        #Then call it, and report any issues!
                        callback.call()
                    except Exception as e:
                        #Naughty Naughty, little callback!
                        logging.error("Exception calling callback on event " + event["event"] + ": " + str(e))
    logging.info("Refreshed events for subsystem " + subsystem)


def cleanup_events(subsystem=None):
    """
    Purge the event system of all callbacks and active_events related to subsystem.
    If subsystem is not specified, then purge for all subsystems
    """
    #Purge active_events:
    #For each active event
    for event in _active_events[:]:
        #If it was started by subsystem
        if event["src_subsystem"] is subsystem or subsystem is None:
            #Stop it!
            stop_event(event["event"], "events")

    #Purge callbacks
    #For each event
    for event in _event_callbacks:
        #For each callback in that event
        #The "[:]" copies the list, so we are not deleting objects from the same list as we are iterating over.
        for callback in _event_callbacks[event][:]:
            #If we have a match, check if it is an active event, and call it's inverse callback if so!
            if callback.subsystem is subsystem or subsystem is None:
                #Is this event an active event?
                if event in [x["event"] for x in _active_events]:
                    #If so, call it's inverse callback
                    callback.call_inverse()
                #Purge it!
                _event_callbacks[event].remove(callback)