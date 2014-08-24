__author__ = 'christian'
import threading
import logging
import time


class module(object):

    name = "ModuleBase"
    stopFlag = False
    eventCallbacks = dict()

    def callFunc(self, function, args, kwargs, finEvent):
        function(*args, **kwargs)
        finEvent.set()

    def onEvent(self, event, callback):
        if self.eventCallbacks.setdefault(event) is None:
                self.eventCallbacks[event] = list()
        self.eventCallbacks[event].append(callback)

    def setEvent(self, event):
        if self.eventCallbacks.setdefault(event) is None:
            return
        for callback in self.eventCallbacks[event]:
            callback()
        print(self.name + ": Event Triggered: " + event)

    def moduleLoad(self):
        pass

    def moduleUnload(self):
        self.stopFlag = True

    def __getattribute__(self, item):
        attribute = object.__getattribute__(self, item)
        if item is "callFunc":
            return attribute
        if hasattr(attribute, "__call__"):
            #Object is function
            return funcWrap(attribute, self)
        else:
            return attribute


class funcWrap:
    def __init__(self, attribute, module):
        self.attribute = attribute
        self.module = module

    def __call__(self, *args, **kwargs):
        finished = threading.Event()
        compiledArgs = (self.attribute, args, kwargs, finished)
        target = self.module.callFunc
        thread = threading.Thread(target=target, args=compiledArgs)
        thread.start()
        return finished
