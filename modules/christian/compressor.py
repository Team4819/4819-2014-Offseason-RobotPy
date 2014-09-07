from framework import modbase
from framework.refrence_db import get_ref
try:
    import wpilib
except ImportError:
    from pyfrc import wpilib

__author__ = 'christian'


class Module(modbase.Module):
    name = "compressor"

    def module_load(self):
        self.compressor = get_ref("compressor", wpilib.Compressor, 14, 1)
        self.compressor.Start()

