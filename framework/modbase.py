import threading
__author__ = 'christian'


class Module(object):

    name = "ModuleBase"
    wants = list()
    stop_flag = False
    eventCallbacks = dict()
    dataStreams = dict()

    def call_func(self, function, args, kwargs, finish):
        function(*args, **kwargs)
        finish.set()

    def module_load(self):
        pass

    def module_unload(self):
        self.stop_flag = True

    def start(self):
        pass

    def __getattr__(self, item):
        if item is "Async":
            return _Async(self)


class _Async:
    def __init__(self, module):
        self.module = module

    def __getattr__(self, item):
        attribute = getattr(self.module, item)
        return _FuncWrap(attribute, self.module)


class _FuncWrap:
    def __init__(self, attribute, module):
        self.attribute = attribute
        self.module = module

    def __call__(self, *args, **kwargs):
        finished = threading.Event()
        compiled_args = (self.attribute, args, kwargs, finished)
        target = self.module.call_func
        thread = threading.Thread(target=target, args=compiled_args)
        thread.start()
        return finished
