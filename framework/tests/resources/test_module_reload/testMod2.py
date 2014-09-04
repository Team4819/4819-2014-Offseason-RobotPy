__author__ = 'christian'
from framework import modbase

class Module(modbase.Module):
    name = "test"

    def getMessage(self):
        return "hello there most excellent tester!"