__author__ = 'christian'
refrences = dict()


class refrence(object):
    def __init__(self):
        self.ref = None


def get_ref(name):
    if name not in refrences:
        refrences[name] = refrence()
    return refrences[name]