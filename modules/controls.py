__author__ = 'christian'
from modules import ModBase
try:
    import wpilib
except ImportError:
    from pyfrc import wpilib

class module(ModBase.module):
    name = "controls"

    DriveX = 0
    DriveY = 0

