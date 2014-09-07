__author__ = 'christian'
refrences = dict()


def get_ref(name, object, *args, **kwargs):
    if name not in refrences:
        ref = object(*args, **kwargs)
        refrences[name] = ref
    else:
        ref = refrences[name]
    return ref