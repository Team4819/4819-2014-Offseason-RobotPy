__author__ = 'christian'

from framework import modbase

class Module(modbase.Module):
    name = "exceptional"
    message = "hi"

    def setMessage(self):
        self.message = "Problem solved!"
