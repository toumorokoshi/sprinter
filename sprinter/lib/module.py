import inspect
import imp
import sys

from .exception import SprinterException


def get_subclass_from_module(module, parent_class):
    """
    Get a subclass of parent_class from the module at module

    get_subclass_from_module performs reflection to find the first class that
    extends the parent_class in the module path, and returns it.
    """
    try:
        r = __recursive_import(module)
        member_dict = dict(inspect.getmembers(r))
        sprinter_class = parent_class
        for v in member_dict.values():
            if inspect.isclass(v) and issubclass(v, parent_class) and v != parent_class:
                if sprinter_class is parent_class:
                    sprinter_class = v
        if sprinter_class is None:
            raise SprinterException("No subclass %s that extends %s exists in classpath!" % (module, str(parent_class)))
        return sprinter_class
    except ImportError:
        e = sys.exc_info()[1]
        raise e


def __recursive_import(module_name):
    """
    Recursively looks for and imports the names, returning the
    module desired

    >>> __recursive_import("sprinter.formulas.unpack") # doctest: +ELLIPSIS
    <module 'unpack' from '...'>

    currently module with relative imports don't work.
    """
    names = module_name.split(".")
    path = None
    module = None
    while len(names) > 0:
        if module:
            path = module.__path__
        name = names.pop(0)
        (module_file, pathname, description) = imp.find_module(name, path)
        module = imp.load_module(name, module_file, pathname, description)
    return module
