__author__ = 'christian'

from framework import modbase

class Module(modbase.Module):
    subsystem = "exceptional"
    message = "hi"

    def setMessage(self):
        self.message = "Problem solved!"
