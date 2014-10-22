import logging
from . import events
from .record import recorder

__author__ = 'christian'

streams = dict()


class LockError(Exception):
    pass


class Datastream(object):

    def __init__(self, name):
        self.name = name
        self.data = None
        self._lock = None
        self.updateHooks = dict()

    def lock(self, owner):
        self._lock = owner

    def get(self, default):
        if self.data is None:
            return default
        else:
            return self.data

    def push(self, data, srcmod, autolock=False):
        if data == self.data:
            return
        if autolock:
            self._lock = srcmod
        if self._lock is not None and self._lock is not srcmod:
            raise LockError(self.name, "No lock for source " + srcmod + ", lock is currently for " + self._lock)
        else:
            olddata = self.data
            if olddata is None:
                olddata = data
            self.data = data
            recorder.update_datastream(self.name, data, srcmod, autolock)
            for key in self.updateHooks:
                try:
                    if self.updateHooks[key](olddata, data):
                        events.trigger_event(key, "datastream." + srcmod)
                except Exception as e:
                    logging.error(e)

    def on_update(self, event, check=lambda x, y: True):
        self.updateHooks[event] = check


def get_stream(stream):
    if stream not in streams:
        streams[stream] = Datastream(stream)
    return streams[stream]


def purge_datastreams():
    while len(streams) is not 0:
        streams.popitem()