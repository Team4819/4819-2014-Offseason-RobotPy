from framework import ModBase
try:
    import wpilib
except ImportError:
    from pyfrc import wpilib

__author__ = 'christian'

class module(ModBase.module):
    name = "compressor"

    def moduleLoad(self):
        self.compressor = wpilib.Compressor(14, 1)
        self.compressor.Start()

