"""
The install script for a sprinter-based setup script.
"""
import shutil
import sys
import argparse
from sprinter.lib import get_recipe_class
from sprinter.environment import Environment

description = \
"""
Install an environment as specified in a sprinter config file
"""

parser = argparse.ArgumentParser(description=description)
parser.add_argument('command', metavar='C',
                    help="The operation that sprinter should run (install, deactivate, activate, switch)")
parser.add_argument('target', metavar='T', help="The path to the manifest file to install")
parser.add_argument('--namespace', dest='namespace', default=None,
                    help="Namespace to check environment against")


def main():
    args = parser.parse_args()
    command = args.command.lower()
    if command == "install":
        e = Environment(namespace=args.namespace)
        e.load_manifest(args.target)
        e.logger.info("Installing %s environment..." % e.namespace)
        __install(e)
        install_sprinter(e)
        e.finalize()
    elif command == "deactivate":
        pass
    elif command == "activate":
        pass
    elif command == "switch":
        pass
    elif command == "remove":
        e = Environment(namespace=args.namespace)
        e.load_namespace(args.target)
        e.logger.info("Completely removing %s..." % e.namespace)
        __remove(e)
    elif command == "update":
        e = Environment(namespace=args.namespace)
        e.load_namespace(args.target)
        if e.load_target_implicit():
            e.logger.info("Updating %s" % e.namespace)
            __install(e)
            install_sprinter(e)
            e.finalize()
    elif command == "reload":
        e = Environment(namespace=args.namespace)
        e.load_namespace(args.target)
        e.logger.info("Reloading %s" % e.namespace)
        recipe_dict = {}
        [__reload(e, name, config, recipe_dict) for name, config in e.reloads().items()]
        e.finalize()


def __install(environment):
    recipe_dict = {}  # a dictionary of recipe objects to perform operations with
    # perform setups
    [__setup(environment, name, config, recipe_dict) for name, config in environment.setups().items()]
    # perform updates
    [__update(environment, name, config, recipe_dict) for name, config in environment.updates().items()]
    # perform destroys
    [__destroy(environment, name, config, recipe_dict) for name, config in environment.destroys().items()]


def __deactivate(environment):
    pass


def __activate(environment):
    pass


def __remove(environment):
    recipe_dict = {}  # a dictionary of recipe objects to perform operations with
    [__destroy(environment, name, config, recipe_dict) for name, config in environment.destroys().items()]
    environment.logger.info("Completely removing %s directory" % environment.namespace)
    shutil.rmtree(environment.directory.root_dir)


def __get_recipe_instance(recipe_dict, recipe, environment):
    """
    get an instance of the recipe object object if it exists, else
    create one, add it to the dict, and pass return it.
    """
    if recipe not in recipe_dict:
        recipe_dict[recipe] = get_recipe_class(recipe, environment)
    return recipe_dict[recipe]


def __setup(environment, name, config, recipe_dict):
    environment.logger.info("Setting up %s..." % name)
    recipe_instance = __get_recipe_instance(recipe_dict,
                                            config['target']['recipe'],
                                            environment)
    recipe_instance.setup(name, config['target'])


def __update(environment, name, config, recipe_dict):
    environment.logger.info("Updating %s..." % name)
    recipe_instance = __get_recipe_instance(recipe_dict,
                                            config['target']['recipe'],
                                            environment)
    recipe_instance.update(name, config)


def __destroy(environment, name, config, recipe_dict):
    environment.logger.info("Destroying %s..." % name)
    recipe_instance = __get_recipe_instance(recipe_dict,
                                            config['source']['recipe'],
                                            environment)
    recipe_instance.destroy(name, config['source'])


def __reload(environment, name, config, recipe_dict):
    environment.logger.info("Reloading %s..." % name)
    recipe_instance = __get_recipe_instance(recipe_dict,
                                            config['source']['recipe'],
                                            environment)
    recipe_instance.reload(name, config['source'])


def install_sprinter(environment):
    environment.inject("~/.bash_profile",
       "[[ -s '%s' ]] && source %s" % (environment.rc_path(), environment.rc_path()))

if __name__ == '__main__':
    if len(sys.argv) > 0 and sys.argv[1] == 'doctest':
        import doctest
        doctest.testmod()
    else:
        main()
