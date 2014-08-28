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
        self.compressor = get_ref("compressor")
        if self.compressor.ref is None:
            self.compressor.ref = wpilib.Compressor(14, 1)

        self.compressor.ref.Start()

