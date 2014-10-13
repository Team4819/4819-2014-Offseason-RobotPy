__author__ = 'christian'
from framework import modbase

class Module(modbase.Module):
    subsystem = "test"

    def getMessage(self):
        return "Get out of here!"