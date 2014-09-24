__author__ = 'christian'


class Module(object):

    name = "generic"
    stop_flag = False

    def module_load(self):
        pass

    def module_unload(self):
        self.stop_flag = True