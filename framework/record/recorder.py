from framework import filesystem
import time
import os
import json

__author__ = 'christian'


datastream_files = dict()
last_datastream_updates = dict()
starttime = 0
datastream_rate = .25

recording = False


def startRecording():
    global recording, starttime, event_file
    filesystem.make_dirs()
    event_file = open(filesystem.events_file, "w", 1)
    recording = True
    starttime = time.clock()


def log_event(action, eventname, srcmod):
    if not recording:
        return
    timestamp = time.clock() - starttime
    event_file.write("Event [{}], Action [{}], Timestamp [{:.2}], From [{}]\n".format(eventname, action, timestamp, srcmod))


def update_datastream(name, data, srcmod, autolock):
    if not recording:
        return
    if name not in datastream_files:
        filename = os.path.join(filesystem.datastream_dir, name + ".rec")
        datastream_files[name] = open(filename, "w", 1)
        last_datastream_updates[name] = 0
    timestamp = time.clock() - starttime
    if last_datastream_updates[name] + datastream_rate < timestamp:
        jsondata = json.dumps(data)
        datastream_files[name].write("Datastream update: Timestamp [{:.2}], From [{}], Autolock [{}], Data [{}]\n".format(timestamp, srcmod, autolock, jsondata))
        last_datastream_updates[name] = timestamp








