"""
    This provides a common interface for sharing data between modules.
"""
__author__ = 'christian'

#This is the dictionary of all streams
_streams = dict()


class LockError(Exception):
    """This is raised when something tries to push to a stream that is locked by something else"""
    pass


class Datastream(object):
    """
        This is used to share variables between modules, it has a write-lock mechanism to prevent multiple things
        from trying to push to it simultaneously.
    """

    def __init__(self, name):

        #The name of the datastream
        self.name = name

        #The data passed to the datastream
        self._data = None

        #The name of the subsystem with a lock on the stream
        self._lock = None

    def lock(self, subsystem):
        """Set the lock of the datastream to subsystem"""
        self._lock = subsystem

    def get(self, default):
        """If we have data, return it."""
        if self._data is None:
            return default
        else:
            return self._data

    def push(self, data, subsystem, autolock=False):
        """
            This pushes data onto the stream, records it as done by subsystem, and locks the stream
            if autolock is set to True
        """

        #Do I recognize this?
        if data == self._data:
            return

        #Check to see if we should automatically lock the stream to subsystem
        if autolock:
            self.lock(subsystem)

        #Check lock
        if self._lock is not None and self._lock is not subsystem:
            raise LockError(self.name, "No lock for source " + subsystem + ", lock is currently for " + self._lock)

        #Set the data and record it
        else:
            self._data = data


def get_stream(stream):
    """Returns a stream with the name stream, creating one if necessary """
    if stream not in _streams:
        _streams[stream] = Datastream(stream)
    return _streams[stream]


def purge_datastreams():
    """Deletes all datastreams"""
    while len(_streams) is not 0:
        _streams.popitem()