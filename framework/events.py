"""
This is an event system. Modules can add callbacks to events, which will be run in a new thread once triggered.
This is the primary mechanism for starting and stopping run loops.

Events can be either "triggered" which is a one-time call (For example: shoot_cannon or reset_gyro),
 or they can be started and then stopped, for events with duration (For example: run, teleoperated, or enabled).
 The main difference is that when modules are freshly loaded, the repeat_callbacks method is called, which then finds all
 of the "active" events and calls them for the new module.
"""
import logging
import threading
import framework.module_engine
__author__ = 'christian'

#This stores references to all created events
events = dict()


class Event(object):
    """This manages everything related to an event"""

    #The event's name
    name = ""
    #Is the event active
    active = False

    class Task(object):
        """
        This is used to store a reference to a callback function and to manage its state.
        it is also the first argument passed to callback functions
        """

        #Is the task currently active?
        #This is different than the event level's active value, since individual tasks
        # can be stopped for module unload
        active = False

        def __init__(self, event, target_subsystem, function):
            self.event = event
            self.target_subsystem = target_subsystem
            self.function = function

        def run(self):
            """Spawn a new thread with the task function."""
            call_wrap = framework.module_engine.get_modules(self.target_subsystem).call_wrap
            threading.Thread(target=call_wrap, args=(self.function, self)).start()

    def __init__(self, name):
        #Initialize variables
        self.name = name
        self._callbacks = list()
        self._inverse_callbacks = list()

    def add_callback(self, target_subsystem, callback):
        """Registers the callback with subsystem as target_subsystem"""
        self._callbacks.append(self.Task(self, target_subsystem, callback))

    def add_inverse_callback(self, target_subsystem, inverse_callback):
        """Registers the inverse callback with subsystem as target_subsystem"""
        self._inverse_callbacks.append(self.Task(self, target_subsystem, inverse_callback))

    def trigger(self, src_subsystem):
        """Starts all callbacks"""
                #Loops through all callbacks and first sets them as active, then runs them
        for callback in self._callbacks:
            callback.active = True
            callback.run()

        #Log it if we actually did anything
        if len(self._callbacks) is not 0:
            logging.info("Triggered event {} by subsystem {}".format(self.name, src_subsystem))

    def start(self, src_subsystem):
        """Starts all callbacks and sets _active to True"""
        #Loops through all callbacks and first sets them as active, then runs them
        for callback in self._callbacks:
            callback.active = True
            callback.run()

        #Log it if we actually did anything
        if len(self._callbacks) is not 0:
            logging.info("Started event {} by subsystem {}".format(self.name, src_subsystem))

        #Set ourself to active
        self.active = True

    def stop(self, src_subsystem):
        """Starts all inverse callbacks and sets _active to False"""

        did_something = False

        #Set all callbacks to inactive
        for callback in self._callbacks:
            did_something = did_something or callback.active
            callback.active = False

        #Run all inverse_callbacks
        for callback in self._inverse_callbacks:
            did_something = True
            callback.run()

        #Log it if we did something
        if did_something:
            logging.info("Stopped event {} by subsystem {}".format(self.name, src_subsystem))
        self.active = False

    def remove_callbacks(self, target_subsystem=None):
        """
        Removes callback records. If target_subsystem is specified,
        restricts removal to that subsystem, otherwise it removes all callbacks.
        """
        #For each callback, if either the subsystem matches, or we have been given no subsystem:
        for callback in self._callbacks[:]:
            if target_subsystem is callback.target_subsystem or target_subsystem is None:
                #Deactivate the callback and remove it from our list.
                callback.active = False
                self._callbacks.remove(callback)

    def repeat_callbacks(self, target_subsystem):
        """Repeats all callbacks pointing to target_subsystem if we are active"""
        #If we are active
        if self.active:
            #Loop through all callbacks that match the target_subsystem and run them
            for callback in [c for c in self._callbacks if c.target_subsystem is target_subsystem]:
                callback.run()


def _get_event(name):
    """Look for event event name, and create one if it does not exist. Then return it."""
    if name not in events:
        events[name] = Event(name)
    return events[name]


def add_callback(event_name, target_subsystem, callback):
    """Set a callback for a specified event, target module, and callback function"""
    #Get the event and add the callback
    _get_event(event_name).add_callback(target_subsystem, callback)


def add_inverse_callback(event_name, target_subsystem, callback):
    """Set an inverse callback for a specified event, target module, and callback function"""
    #Get the event and add the callback
    _get_event(event_name).add_inverse_callback(target_subsystem, callback)


def start_event(event_name, src_subsystem):
    """Starts the event event_name"""
    #Get the event and start it.
    _get_event(event_name).start(src_subsystem)


def stop_event(event_name, src_subsystem):
    """Stop the event event_name"""
    #Get the event and stop it.
    _get_event(event_name).stop(src_subsystem)


def trigger_event(event_name, src_subsystem):
    """Trigger all callbacks for event event_name"""
    #Get the event and trigger it.
    _get_event(event_name).trigger(src_subsystem)


def repeat_callbacks(target_subsystem):
    """Repeats all active callbacks pointed to this subsystem"""
    #Call repeat_callbacks on all events
    for event in events:
        events[event].repeat_callbacks(target_subsystem)
    logging.info("Refreshed callbacks for subsystem " + target_subsystem)


def remove_callbacks(target_subsystem=None):
    """
    Purge the event system of all callbacks and active_events related to subsystem.
    If subsystem is not specified, then purge for all subsystems
    """
    #Call remove_callbacks on all events
    for event in events:
        events[event].remove_callbacks(target_subsystem)
    if target_subsystem is None:
        logging.info("Removed callbacks all subsystems")
    else:
        logging.info("Removed callbacks for subsystem " + target_subsystem)