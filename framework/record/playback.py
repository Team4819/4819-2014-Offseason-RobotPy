from framework import modmaster, datastreams
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
        times = os.listdir(rootdir + "/" + dates[0])
        if len(times) <= 1:
            del(dates[0])
            times = os.listdir(rootdir + "/" + dates[0])
        times.sort(reverse=True)
        recpath = rootdir + "/" + dates[0] + "/" + times[1]

    global starttime
    logging.info("Playing recording at " + recpath)
    starttime = time.monotonic()
    threading.Thread(target=replay_datastreams, args={recpath + "/datastreams"}).start()


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
            if update["srcmod"] in modmaster.list_modules():
                continue
            update["autolock"] = bool(splitdata[2][10:].strip()[1:-1])
            jsondata = splitdata[3][6:].strip()[1:-1]
            update["data"] = json.loads(jsondata)
            parsed_streams[name].append(update)
    #do it
    for stream in parsed_streams:
        stream_handles[stream] = datastreams.get_stream(stream)

    while not finished:
        timestamp = time.monotonic() - starttime
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