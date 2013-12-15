"""
Methods to manipulate the global configuration
"""
import logging
import os

from six.moves import configparser

from sprinter.lib import system
from sprinter import lib
from sprinter.core.templates import warning_template

logger = logging.getLogger(__name__)

# http://www.gnu.org/software/bash/manual/bashref.html#Bash-Startup-Files
# http://zsh.sourceforge.net/Guide/zshguide02.html
SHELL_CONFIG = {
    'bash': {
        'rc': ['.bashrc'],
        'env': ['.bash_profile', '.bash_login', '.profile']
    },
    'zsh': {
        'rc': ['.zshrc'],
        'env': ['.zprofile', '.zlogin']
    },
    'gui': {
        'debian': ['.profile'],
        'osx': lib.insert_environment_osx
    }
}


def load_global_config(config_path):
    """ Load a global configuration object, and query for any required variables along the way """
    config = configparser.RawConfigParser()
    if os.path.exists(config_path):
        logger.info("Checking and setting global parameters...")
        config.read(config_path)
    else:
        _initial_run()
        logger.info("Unable to find a global sprinter configuration!")
        logger.info("Creating one now. Please answer some questions" +
                    " about what you would like sprinter to do.")
        logger.info("")
    # checks and sets sections
    if not config.has_section('global'):
        config.add_section('global')

    if not config.has_section('shell'):
        _configure_shell(config)

    if not config.has_option('global', 'env_source_rc'):
        _configure_env_source_rc(config)

    return config


def create_default_config():
    """ Create a default configuration object, with all parameters filled """
    config = configparser.RawConfigParser()
    config.add_section('global')
    config.set('global', 'env_source_rc', False)
    config.add_section('shell')
    config.set('shell', 'bash', "true")
    config.set('shell', 'zsh', "true")
    config.set('shell', 'gui', "true")
    return config


def _initial_run():
    """ Check things during the initial setting of sprinter's global config """
    if system.is_officially_supported():
        logger.warn(warning_template
                    + "===========================================================\n"
                    + "Sprinter is not officially supported on {0}! Please use at your own risk.\n\n".format(system.operating_system())
                    + "You can find the supported platforms here:\n"
                    + "(http://sprinter.readthedocs.org/en/latest/index.html#compatible-systems)\n\n"
                    + "Conversely, please help us support your system by reporting on issues\n"
                    + "(http://sprinter.readthedocs.org/en/latest/faq.html#i-need-help-who-do-i-talk-to)\n"
                    + "===========================================================")


def _configure_shell(config):
    """ Checks and queries values for the shell """
    config.add_section('shell')
    logger.info("What shells or environments would you like sprinter to work with?\n" +
                "(Sprinter will not try to inject into environments not specified here.)\n" +
                "If you specify 'gui', sprinter will attempt to inject it's state into graphical programs as well.\n" +
                "i.e. environment variables sprinter set will affect programs as well, not just shells")
    environments = list(enumerate(sorted(SHELL_CONFIG), start=1))
    logger.info("[0]: All, " + ", ".join(["[%d]: %s" % (index, val) for index, val in environments]))
    desired_environments = lib.prompt("type the environment, comma-separated", default="0")
    for index, val in environments:
        if str(index) in desired_environments or "0" in desired_environments:
            config.set('shell', val, 'true')
        else:
            config.set('shell', val, 'false')


def _configure_env_source_rc(config):
    """ Configures wether to have .env source .rc """
    config.set('global', 'env_source_rc', False)
    if system.is_osx():
        logger.info("On OSX, login shells are default, which only source sprinter's 'env' configuration.")
        logger.info("I.E. environment variables would be sourced, but not shell functions "
                    + "or terminal status lines.")
        logger.info("The typical solution to get around this is to source your rc file (.bashrc, .zshrc) "
                    + "from your login shell.")
        env_source_rc = lib.prompt("would you like sprinter to source the rc file too?", default="yes",
                                   boolean=True)
        config.set('global', 'env_source_rc', env_source_rc)
