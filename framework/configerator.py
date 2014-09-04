__author__ = 'christian'
import logging
parsed_config = dict()
loaded = False


def get_config(config="modules/mods.conf"):
    global loaded
    if not loaded:
        parse_config(config)
        loaded = True
    return parsed_config


def parse_config(path):
    f = open(path)
    section = None
    for line in f:
        line = line.rstrip('\r\n')
        if "#" in line:
            line, comment = line.split("#", 1)
        if "[" in line:
            section = line.split("[", 1)[1].split("]", 1)[0]
            parsed_config[section] = list()
        else:
            if line is not "":
                parsed_config[section].append(line)
    logging.info("Finished parsing " + path)