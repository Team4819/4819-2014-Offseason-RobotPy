import time
import os
import json

__author__ = 'christian'


events_file = "events.rec"
datastream_files = dict()
last_datastream_updates = dict()
starttime = 0
log_dir = os.path.join("recs", time.strftime("%m.%d.%y/%X"))
datastream_dir = os.path.join(log_dir, "datastreams")
datastream_rate = .25
os.makedirs(log_dir, exist_ok=True)

recording = False


def startRecording():
    global recording, starttime, event_file
    filename = os.path.join(log_dir, events_file)
    event_file = open(filename, "w", 1)
    os.makedirs(datastream_dir, exist_ok=True)
    recording = True
    starttime = time.monotonic()


def log_event(action, eventname, srcmod):
    if not recording:
        return
    timestamp = time.monotonic() - starttime
    event_file.write("Event [{}], Action [{}], Timestamp [{:.2}], From [{}]\n".format(eventname, action, timestamp, srcmod))


def update_datastream(name, data, srcmod, autolock):
    if not recording:
        return
    if name not in datastream_files:
        filename = os.path.join(datastream_dir, name + ".rec")
        datastream_files[name] = open(filename, "w", 1)
        last_datastream_updates[name] = 0
    timestamp = time.monotonic() - starttime
    if last_datastream_updates[name] + datastream_rate < timestamp:
        jsondata = json.dumps(data)
        datastream_files[name].write("Datastream update: Timestamp [{:.2}], From [{}], Autolock [{}], Data [{}]\n".format(timestamp, srcmod, autolock, jsondata))
        last_datastream_updates[name] = timestamp








