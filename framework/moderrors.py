import logging

__author__ = 'christian'


class ModuleLoadError(Exception):
    def __init__(self, name, message):
        logging.error("Module Load Error: " + name + ": " + message)


class ModuleUnloadError(Exception):
    def __init__(self, name, message):
        logging.error("Module Unload Error: " + name + ": " + message)