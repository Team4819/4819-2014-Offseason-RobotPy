from framework import ModBase

__author__ = 'christian'
try:
    import wpilib
except ImportError:
    from pyfrc import wpilib

class module(ModBase.module):
    name = "controls"

    DriveX = 0
    DriveY = 0

