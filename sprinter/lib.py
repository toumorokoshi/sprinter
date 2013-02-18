"""
Library module for sprinter. To handle a lot of the typical
features of the library.

"""
import inspect
import imp
import os
import re
import subprocess

from sprinter.recipebase import RecipeBase


def get_recipe_class(recipe, environment):
    """
    Get the recipe name and return an instance The recipe path is a
    path to the module. get_recipe_class performs reflection to find
    the first class that extends recipebase, and that is the class
    that an instance of it gets returned.

    >>> issubclass(get_recipe_class("sprinter.recipes.unpack").__class__, RecipeBase)
    True
    """
    try:
        r = __recursive_import(recipe)
        member_dict = dict(inspect.getmembers(r))
        for v in member_dict.values():
            if inspect.isclass(v) and issubclass(v, RecipeBase) and v != RecipeBase:
                return v(environment)
        raise Exception("No recipe %s exists in classpath!" % recipe)
    except ImportError as e:
        raise e


def call(command):
    args = command.split(" ")
    subprocess.call(args)


def __recursive_import(module_name):
    """
    Recursively looks for and imports the names, returning the
    module desired

    >>> __recursive_import("sprinter.recipes.unpack") # doctest: +ELLIPSIS
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

if __name__ == '__main__':
    import doctest
    doctest.testmod()
