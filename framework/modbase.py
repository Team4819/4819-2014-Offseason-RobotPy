import logging
__author__ = 'christian'


class Module(object):

    name = "generic"
    stop_flag = False

    def module_load(self):
        pass

    def module_unload(self):
        self.stop_flag = True

    def start(self):
        pass

    def __getattr__(self, item):
        return CallReporter(self.name, item)


class CallReporter:
    def __init__(self, module, item):
        self.module = module
        self.item = item

    def __call__(self, *args, **kwargs):
        logging.error("Functon call to non-existent function " + self.item + " on module " + self.module)