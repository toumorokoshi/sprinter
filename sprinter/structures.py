"""
A location for various structs/class bases
"""


class Singleton(type):
    """
    A basic singleton to be used as a metaclass
    
    Credit goes to:
    http://stackoverflow.com/questions/6760685/creating-a-singleton-in-python

    Used as a metaclass, not a base class:

    class MyClass(object):
      __metaclass__ = Singleton
    """
    _instances = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class EnumInstance(object):

    def __init__(self, **kw):
        for k in kw:
            setattr(self, k, kw[k])


# credit goes to http://stackoverflow.com/questions/36932/how-can-i-represent-an-enum-in-python
def Enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    reverse = dict((value, key) for key, value in enums.items())
    values = [v for v in enums.values()]
    enums['values'] = values
    enums['value'] = reverse
    return type('Enum', (), enums)
