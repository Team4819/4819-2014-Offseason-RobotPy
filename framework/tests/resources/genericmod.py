__author__ = 'christian'


class Module(object):

    subsystem = "generic"
    stop_flag = False

    def module_load(self):
        pass

    def module_unload(self):
        self.stop_flag = True