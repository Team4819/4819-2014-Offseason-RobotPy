__author__ = 'christian'
import logging
parsed_config = dict()


def parse_config(path):
    f = open(path)
    section = None
    for line in f:
        line = line.rstrip('\r\n')
        if "#" in line:
            line, comment = line.split("#", 1)
            line = line.strip()
        if "[" in line:
            section = line.split("[", 1)[1].split("]", 1)[0]
            parsed_config[section] = list()
        else:
            if line is not "":
                parsed_config[section].append(line)
    logging.info("Finished parsing " + path)
    return parsed_config