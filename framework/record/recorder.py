from framework import filesystem
import time
import os
import json
from decimal import *

__author__ = 'christian'

#TODO This stuff is currently junk. Everything has changed since this was built, so it will probably blow up if used

datastream_files = dict()
last_datastream_updates = dict()
starttime = 0
datastream_rate = .25

recording = False

TWOPLACES = Decimal(10) ** -2


def startRecording():
    global recording, starttime, event_file
    filesystem.make_dirs()
    event_file = open(filesystem.events_file, "w", 1)
    recording = True
    starttime = time.time()


def log_event(action, eventname, srcmod):
    if not recording:
        return
    timestamp = time.time() - starttime
    event_file.write("Event [{}], Action [{}], Timestamp [{}], From [{}]\n".format(eventname, action, Decimal(timestamp).quantize(TWOPLACES), srcmod))


def update_datastream(name, data, srcmod, autolock):
    if not recording:
        return
    if name not in datastream_files:
        filename = os.path.join(filesystem.datastream_dir, name + ".rec")
        datastream_files[name] = open(filename, "w", 1)
        last_datastream_updates[name] = 0
    timestamp = time.time() - starttime
    if last_datastream_updates[name] + datastream_rate < timestamp:
        jsondata = json.dumps(data)
        datastream_files[name].write("Datastream update: Timestamp [{}], From [{}], Autolock [{}], Data [{}]\n".format(Decimal(timestamp).quantize(TWOPLACES), srcmod, autolock, jsondata))
        last_datastream_updates[name] = timestamp








