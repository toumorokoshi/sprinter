"""
Library module for sprinter. To handle a lot of the typical
features of the library.

"""
import inspect

from sprinter.recipebase import RecipeBase


def get_recipe_class(recipe):
    """
    Get the recipe name and return an instance The recipe path is a
    path to the module. get_recipe_class performs reflection to find
    the first class that extends recipebase, and that is the class
    that an instance of it gets returned.
    >>> issubclass(get_recipe_class("sprinter.recipes.unpack"), RecipeBase)
    True
    """
    try:
        r = __import__(recipe)
        member_dict = dict(inspect.getmembers(r))
        for v in member_dict.values():
            if inspect.isclass(v) and issubclass(v, RecipeBase):
                return v()
        raise Exception("No recipe %s exists in classpath!" % v)
    except ImportError as e:
        raise e
    except Exception as e:
        raise e

if __name__ == '__main__':
    import doctest
    doctest.testmod()
