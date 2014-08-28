from framework import events
import logging
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
        if self._lock is not None and self._lock is not srcmod:
            if autolock:
                self.lock = srcmod
            else:
                raise LockError(self.name, "No lock for source " + srcmod + ", lock is currently for " + self._lock)
        if data is self.data:
            return
        else:
            olddata = self.data
            self.data = data
            for key in self.updateHooks:
                try:
                    if self.updateHooks[key](olddata, data):
                        events.trigger(key, self.name)
                except Exception as e:
                    logging.error(e)

    def on_update(self, event, check=lambda x, y: True):
        self.updateHooks[event] = check
        self._active = True

def get_stream(stream):
    if streams.setdefault(stream) is None:
        streams[stream] = DataStream(stream)
    return streams[stream]

