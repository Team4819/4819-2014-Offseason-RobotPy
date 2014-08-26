__author__ = 'christian'
import threading
from framework import ModMaster
import logging
import time


class module(object):

    name = "ModuleBase"
    wants = list()
    stopFlag = False
    eventCallbacks = dict()
    dataStreams = dict()

    def callFunc(self, function, args, kwargs, finEvent):
        function(*args, **kwargs)
        finEvent.set()

    def triggerEvent(self, event):
        ModMaster.triggerEvent(event, self.name)

    def moduleLoad(self):
        pass

    def setDataStream(self, name, data):
        ModMaster.pushToDataStream(name, data, self.name)

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
