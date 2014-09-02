import time
import os
import json

__author__ = 'christian'


events_file = "events.rec"
datastream_files = dict()
last_datastream_updates = dict()
starttime = 0
log_dir = "recs/" + time.strftime("%m.%d.%y/%X")
datastream_dir = log_dir + "/datastreams"
datastream_rate = .25
os.makedirs(log_dir, exist_ok=True)
os.makedirs(datastream_dir, exist_ok=True)
event_file = open(log_dir + "/" + events_file, "w")
recording = False


def startRecording():
    global recording, starttime
    recording = True
    starttime = time.monotonic()


def log_event(action, eventname, srcmod):
    if not recording:
        return
    timestamp = time.monotonic() - starttime
    event_file.write("Event [" + eventname + "] Action [" + action + "] At [" + str.format("{0:.3f}", timestamp) + "] From [" + srcmod + "]\n")


def update_datastream(name, data, srcmod, autolock):
    if not recording:
        return
    if name not in datastream_files:
        datastream_files[name] = open(datastream_dir + "/" + name + ".rec", "w")
        last_datastream_updates[name] = 0
    timestamp = time.monotonic() - starttime
    if last_datastream_updates[name] + datastream_rate < timestamp:
        jsondata = json.dumps(data)
        datastream_files[name].write("Datastream update: Timestamp [{:.2}], From [{}], Autolock [{}], Data [{}]\n".format(timestamp, srcmod, autolock, jsondata))
        last_datastream_updates[name] = timestamp








