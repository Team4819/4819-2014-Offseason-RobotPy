import logging
from . import events
from .record import recorder

__author__ = 'christian'

streams = dict()


class LockError(Exception):
    pass


class DataStream(object):

    def __init__(self, name):
        self.name = name
        self.data = None
        self._lock = None
        self._active = False
        self.updateHooks = dict()

    def activate(self):
        self._active = True

    def lock(self, owner):
        self._lock = owner

    def get(self, default):
        self._active = True
        if self.data is None:
            return default
        else:
            return self.data

    def push(self, data, srcmod, autolock=False):
        if not self._active:
            return
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
                        events.trigger(key, "datastream")
                except Exception as e:
                    logging.error(e)

    def on_update(self, event, check=lambda x, y: True):
        self.updateHooks[event] = check
        self._active = True


def get_stream(stream, activate=False):
    if stream not in streams:
        streams[stream] = DataStream(stream)
    if activate:
        streams[stream].activate()
    return streams[stream]


def purge_datastreams():
    keys = list()
    keys += streams.keys()
    for key in keys:
        del(streams[key])