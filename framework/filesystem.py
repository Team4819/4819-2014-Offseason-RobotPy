import os
import time
__author__ = 'christian'

root_dir = ""
log_dir = os.path.join(root_dir, "recs")
log_file = os.path.join(log_dir, "main.log")
events_file = os.path.join(log_dir, "events.rec")
datastream_dir = os.path.join(log_dir, "datastreams")
paths_made = False


def gen_paths():
    global log_dir, events_file, log_file, datastream_dir
    log_dir = os.path.join(root_dir, "recs", time.strftime("%m-%d-%y"), time.strftime("%H.%M.%S"))
    log_file = os.path.join(log_dir, "main.log")
    events_file = os.path.join(log_dir, "events.rec")
    datastream_dir = os.path.join(log_dir, "datastreams")


def make_dirs():
    global paths_made
    if paths_made:
        return
    os.makedirs(log_dir, exist_ok=True)
    os.makedirs(datastream_dir, exist_ok=True)
    paths_made = True