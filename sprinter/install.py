"""
The install script for a sprinter-based setup script.
"""
import sys
import argparse
from sprinter.lib import get_recipe_class, install_sprinter
from sprinter.environment import Environment

description = \
"""
Install an environment as specified in a sprinter config file
"""

parser = argparse.ArgumentParser(description=description)
parser.add_argument('command', metavar='C', nargs=1,
                    help="The operation that sprinter should run (install, deactivate, activate, switch)")
parser.add_argument('target', metavar='T', nargs=1, help="The path to the manifest file to install")
parser.add_argument('--namespace', dest='namespace', default=None,
                    help="Namespace to check environment against")


def main():
    args = parser.parse_args()
    command = args.command[0].lower()
    if command == "install":
        e = Environment(args.target[0], namespace=args.namespace)
        e.logger.info("Installing %s environment..." % args.namespace)
        __install(e)
        install_sprinter(e)


def __install(environment):
    recipe_dict = {}  # a dictionary of recipe objects to perform operations with
    # perform setups
    [__setup(environment, name, config, recipe_dict) for name, config in environment.setups().items()]
    # perform updates
    [__update(environment, name, config, recipe_dict) for name, config in environment.updates().items()]
    # perform destroys
    [__destroy(environment, name, config, recipe_dict) for name, config in environment.destroys().items()]


def __get_recipe_instance(recipe_dict, recipe):
    """
    get an instance of the recipe object object if it exists, else
    create one, add it to the dict, and pass return it.
    """
    if recipe not in recipe_dict:
        recipe_dict[recipe] = get_recipe_class(recipe)
    return recipe_dict[recipe]


def __setup(environment, name, config, recipe_dict):
    environment.logger.info("Setting up %s..." % name)
    recipe_instance = __get_recipe_instance(recipe_dict, config['target']['recipe'])
    recipe_instance.setup(environment, name, config['target'])


def __update(environment, name, config, recipe_dict):
    environment.logger.info("Updating %s..." % name)
    recipe_instance = __get_recipe_instance(recipe_dict, config['target']['recipe'])
    recipe_instance.update(environment, name, config)


def __destroy(environment, name, config, recipe_dict):
    environment.logger.info("Destroying %s..." % name)
    recipe_instance = __get_recipe_instance(recipe_dict, config['source']['recipe'])
    recipe_instance.destroy(environment, name, config['source'])

if __name__ == '__main__':
    if len(sys.argv) > 0 and sys.argv[1] == 'doctest':
        import doctest
        doctest.testmod()
    else:
        main()
