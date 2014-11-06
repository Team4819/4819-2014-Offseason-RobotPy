"""
This manages fs stuff, as the filename says :).
It contains utilities for parsing config files, creating log file directories, and other miscellaneous things.
"""

import logging
import os
__author__ = 'christian'

#The root directory of the python tree
root_dir = ""

#The directory to store all logs and recordings from this run session
log_dir = os.path.join(root_dir, "logs")

#The log file, which is a dump of all console output
log_file = os.path.join(log_dir, "main.log")

#The .rec file for events
events_file = os.path.join(log_dir, "events.rec")

#The directory to store all datastream recordings
datastream_dir = os.path.join(log_dir, "datastreams")

#Have we mkdir'd?
paths_made = False

#The parsed config file
parsed_config = dict()


def gen_paths():
    """Generate the paths for all files used by the framework, from the root dir."""
    global log_dir, events_file, log_file, datastream_dir

    #The root log directory
    log_root_dir = os.path.join(root_dir, "logs")

    #Figure out what log file index we should use
    #The log file index is a 4-digit number corresponding to an unused log folder
    index = 0
    #If our base log_root_dir exists:
    if os.path.exists(log_dir):

        #Get existing folders, convert to string list, and sort
        folders = os.listdir(log_dir)
        ids = [int(f) for f in folders]
        ids.sort()

        #This algorithim determines the next sequential value for our log index, it scans through the existing numbers
        #until either it finds a missing number in sequence, or runs out of numbers to scan.

        #Set this to a high number to start with, as it will get set every loop iteration
        last_id = 10000
        for present_index in ids:
            #If we have a break in the number sequence, abort and use what we have
            if present_index > last_id + 1:
                break
            #If we have found a bigger number to use for index
            if present_index > index:
                index = present_index

            last_id = present_index

        #Convert from largest existing index to the index we should use!
        index += 1

    #Set the log_dir, which is the directory for storing all logs during this run session
    log_dir = os.path.join(log_dir, str(index).zfill(4))

    #Set the log_file, which is a dump of all console output
    log_file = os.path.join(log_dir, "main.log")

    #Set the events_file, which is where all events are recorded
    events_file = os.path.join(log_dir, "events.rec")

    #Set the datastream_dir, within which all datastreams are recorded
    datastream_dir = os.path.join(log_dir, "datastreams")


def make_dirs():
    """Actually make the directories for use!"""
    global paths_made

    #Have we done this already? Then why are we trying to do it again?
    if paths_made:
        return

    #Make the dirs
    os.makedirs(log_dir, exist_ok=True)
    os.makedirs(datastream_dir, exist_ok=True)
    paths_made = True


def init_logs():
    """Start up the logging output to the log file"""

    #Ensure that the directories are made
    make_dirs()

    #Create FileHandler logging handler, set it's log level, configure the log storage format,
    #  and add the formatter to the root logger
    fh = logging.FileHandler(log_file)
    fh.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logging.root.addHandler(fh)
    logging.root.setLevel(logging.INFO)

    #Report it to the world!
    logging.info("Saving logs to " + log_file)


def parse_config(path):
    """Parse the module config file, returns a dictionary of all config file entries"""
    #Open the file
    f = open(path)
    section = None

    #for each line in file:
    for line in f:
        #Get rid of extra spaces and carridge-returns
        line = line.rstrip('\r\n')

        #If there is a comment on the line, get rid of everything after the comment symbol and trim whitespace
        #Example: hi there #This is a comment
        if "#" in line:
            line, comment = line.split("#", 1)
            line = line.strip()

        #If there is a section header on the line, figure out what it's name is, and save it
        if "[" in line:
            #Example: [StartupMods]
            section = line.split("[", 1)[1].split("]", 1)[0]
            parsed_config[section] = list()

        #If there is no section header, than the line must contian data, so save it under the current section
        else:
            if line is not "":
                parsed_config[section].append(line)

    #Message the system
    logging.info("Finished parsing " + path)
    return parsed_config