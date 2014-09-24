__author__ = 'christian'
from framework import modbase
import logging


class Module(modbase.Module):

    name = "placeholder"
    target = ""

    def set_target(self, target):
        self.target = target

    def __getattr__(self, item):
        return CallReporter(self.target, item)


class CallReporter:
    def __init__(self, module, item):
        self.module = module
        self.item = item

    def __call__(self, *args, **kwargs):
        logging.warning("Functon call to non-existent function " + self.item + " on module " + self.module)
