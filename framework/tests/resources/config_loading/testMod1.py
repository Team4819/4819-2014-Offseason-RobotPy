__author__ = 'christian'
from framework import modbase

class Module(modbase.Module):
    name = "test1"

    def getMessage(self):
        return "Get out of here!"