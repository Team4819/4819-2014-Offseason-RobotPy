__author__ = 'christian'

class Module:
    subsystem = "exceptional"
    message = "hi"

    def setMessage(self):
        raise Exception("This is Treason!")