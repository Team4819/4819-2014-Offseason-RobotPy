from framework import module_engine, datastreams, events
import json
import logging
import os
import time
import threading

__author__ = 'christian'

starttime = 0


def replay_recording(recpath="latest"):
    if recpath is "latest":
        rootdir = "recs"
        dates = os.listdir(rootdir)
        dates.sort()
        times = os.listdir(os.path.join(rootdir, dates[0]))
        if len(times) <= 1:
            del(dates[0])
            times = os.listdir(os.path.join(rootdir, dates[0]))
        times.sort(reverse=True)
        recpath = os.path.join(rootdir, dates[0], times[1])

    global starttime
    logging.info("Playing recording at " + recpath)
    starttime = time.time()
    threading.Thread(target=replay_datastreams, args={os.path.join(recpath, "datastreams")}).start()
    threading.Thread(target=replay_events, args={os.path.join(recpath, "events.rec")}).start()


def replay_datastreams(datastreampath):
    finished = False
    parsed_streams = dict()
    stream_handles = dict()

    #parse it
    for datastream in os.listdir(datastreampath):
        filehandle = open(datastreampath + "/" + datastream, "r")
        name = datastream.replace(".rec", "")
        parsed_streams[name] = list()
        lines = filehandle.readlines()
        for line in lines:
            line = line.rstrip()
            splitdata = line.split(":", 1)[1].split(",", 3)
            update = dict()
            update["timestamp"] = float(splitdata[0][11:].strip()[1:-1])
            update["srcmod"] = splitdata[1][6:].strip()[1:-1]
            if update["srcmod"] in module_engine.list_modules():
                continue
            update["autolock"] = bool(splitdata[2][10:].strip()[1:-1])
            jsondata = splitdata[3][6:].strip()[1:-1]
            update["data"] = json.loads(jsondata)
            parsed_streams[name].append(update)
    #do it
    for stream in parsed_streams:
        stream_handles[stream] = datastreams.get_stream(stream)

    while not finished:
        timestamp = time.time() - starttime
        finished = True
        for stream in parsed_streams:
            if len(parsed_streams[stream]) is 0:
                continue
            finished = False
            if parsed_streams[stream][0]["timestamp"] < timestamp:
                update = parsed_streams[stream][0]
                del parsed_streams[stream][0]
                stream_handles[stream].push(update["data"], update["srcmod"], autolock=update["autolock"])
        time.sleep(.1)
    logging.info("Datastream Playback finished")


def replay_events(eventsfile):
    finished = False
    parsed_events = list()

    #parse it
    filehandle = open(eventsfile, "r")
    lines = filehandle.readlines()
    for line in lines:
        line = line.rstrip()
        splitdata = line.split(",")
        update = dict()
        update["event"] = splitdata[0][6:].strip()[1:-1]
        update["action"] = splitdata[1][7:].strip()[1:-1]
        update["timestamp"] = float(splitdata[2][11:].strip()[1:-1])
        update["srcmod"] = splitdata[3][5:].strip()[1:-1]
        if update["srcmod"] in module_engine.list_modules() or update["srcmod"] in ("modmaster", "RobotTrunk", "datastream"):
            continue
        parsed_events.append(update)
    logging.info("Parsed events file " + eventsfile)
    #do it
    while not finished:
        timestamp = time.time() - starttime
        if len(parsed_events) is 0:
            finished = True
            continue
        if parsed_events[0]["timestamp"] < timestamp:
            event = parsed_events[0]
            del parsed_events[0]
            if event['action'] == "triggered":
                events.trigger(event["event"], event["srcmod"])
            else:
                events.set_event(event["event"], event["srcmod"], event["action"] is "on")
        time.sleep(.1)
    logging.info("Event Playback finished")