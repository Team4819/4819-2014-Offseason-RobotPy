__author__ = 'christian'
from framework import modbase

class Module(modbase.Module):
    name = "test2"

    def getMessage(self):
        return "Get out of here, Now!"