from framework import modbase
try:
    import wpilib
except ImportError:
    from pyfrc import wpilib

__author__ = 'christian'

class Module(modbase.Module):
    name = "compressor"

    def module_load(self):
        self.compressor = wpilib.Compressor(14, 1)
        self.compressor.Start()

