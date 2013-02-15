"""
The install script for a sprinter-based setup script.
"""
import sys
import argparse
from sprinter.lib import get_recipe_class
from sprinter.manifest import Manifest
from sprinter.directory import Directory

description = \
"""
Install an environment as specified in a sprinter config file
"""

parser = argparse.ArgumentParser(description=description)
parser.add_argument('target', metavar='T', nargs=1, help="The path to the manifest file to install")
parser.add_argument('--namespace', dest='namespace', default=None,
                    help="Namespace to check environment against")


def main():
    args = parser.parse_args()
    m = Manifest(args.target)
    recipe_dict = {}  # a dictionary of recipe objects to perform operations with
    d = Directory(namespace=parser.namespace)
    # perform setups
    [__setup(d, name, config, recipe_dict) for name, config in m.setups().items()]
    # perform updates
    [__update(d, name, config, recipe_dict) for name, config in m.updates().items()]
    # perform destroys
    [__destroy(d, name, config, recipe_dict) for name, config in m.destroys().items()]


def __get_recipe_instance(recipe_dict, recipe):
    """
    get an instance of the recipe object object if it exists, else
    create one, add it to the dict, and pass return it.
    """
    if recipe not in recipe_dict:
        recipe_dict[recipe] = get_recipe_class(recipe)
    return recipe_dict[recipe]


def __setup(directory, name, config, recipe_dict):
    recipe_instance = __get_recipe_instance(recipe_dict, config['target'])
    recipe_instance.setup(directory, name, config)


def __update(directory, name, config, recipe_dict):
    recipe_instance = __get_recipe_instance(recipe_dict, config['target'])
    recipe_instance.update(directory, name, config)


def __destroy(directory, name, config, recipe_dict):
    recipe_instance = __get_recipe_instance(recipe_dict, config['source'])
    recipe_instance.destroy(directory, name, config)

if __name__ == '__main__':
    if len(sys.argv) > 0 and sys.argv[1] == 'doctest':
        import doctest
        doctest.testmod()
    else:
        main()
