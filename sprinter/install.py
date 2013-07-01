"""
The install script for a sprinter-based setup script.
"""
import logging
import os
import signal
import sys
from optparse import OptionParser

from sprinter import lib
from sprinter.environment import Environment
from sprinter.manifest import Manifest
from sprinter.directory import Directory
from sprinter.exceptions import SprinterException, BadCredentialsException

env = None

description = \
"""
Install an environment as specified in a sprinter config file
"""

VALID_COMMANDS = ["install", "update", "remove", "deactivate", "activate",
                  "environments", "validate"]

parser = OptionParser(description=description)
# parser = argparse.ArgumentParser(description=description)
# parser.add_option('command', metavar='C',
#                     help="The operation that sprinter should run (install, deactivate, activate, switch)")
# parser.add_option('target', metavar='T', help="The path to the manifest file to install", nargs='?')
parser.add_option('--namespace', dest='namespace', default=None,
                  help="Namespace to check environment against")
parser.add_option('--username', dest='username', default=None,
                  help="Username if the url requires authentication")
parser.add_option('--auth', dest='auth', action='store_true',
                  help="Specifies authentication is required")
parser.add_option('--password', dest='password', default=None,
                  help="Password if the url requires authentication")
parser.add_option('-v', dest='verbose', action='store_true', help="Make output verbose")
# not implemented yet
parser.add_option('--sandboxbrew', dest='sandbox_brew', default=False,
                  help="if true, sandbox a brew installation, alternatively, " +
                  "false will disable brew sandboxes for configuration that request it.")
parser.add_option('--sandboxaptget', dest='sandbox_aptget', default=False,
                  help="if true, sandbox an apt-get installation, alternatively, " +
                  "false will disable apt-get sandboxes for configuration that request it.")
parser.add_option('--virtualenv', dest='virtualenv', default=False,
                  help="if true, will virtualenv sprinter and install eggs relative to it, " +
                  "false will disable apt-get sandboxes for configuration that request it.")


def signal_handler(signal, frame):
    print "Shutting down sprinter..."
    sys.exit(0)


def main():
    signal.signal(signal.SIGINT, signal_handler)
    try:
        parse_args(sys.argv[1:])
    except SprinterException, e:
        print str(e)
        print "Sprinter shut down with an error!"
    except BadCredentialsException, e:
        print str(e)
        print "Invalid username and password combination!"


def error(message):
    print message
    exit()


def parse_args(argv, Environment=Environment):
    options, args = parser.parse_args(argv)
    if len(args) == 0:
        error("Please enter a sprinter action: %s" % str(VALID_COMMANDS))
    command = args[0].lower()
    if command not in VALID_COMMANDS:
        error("Please enter a valid sprinter action: %s" % ",".join(VALID_COMMANDS))
    target = args[1] if len(args) > 1 else None
    logging_level = logging.DEBUG if options.verbose else logging.INFO
    # start processing commands
    env = Environment(logging_level=logging_level)

    if command == "install":
        def handle_install_shutdown(signal, frame):
            if env.last_phase == "install":
                print "Removing install..."
                env.directory.remove()
                env.clear_environment_rc()
            signal_handler(signal, frame)
        signal.signal(signal.SIGINT, handle_install_shutdown)
        if options.username or options.auth:
            options = get_credentials(options, parse_domain(target))
            target = Manifest(target, username=options.username, password=options.password)
        env.target = target
        env.namespace = options.namespace
        env.install()

    elif command == "update":
        env.directory = Directory(target)
        env.source = Manifest(env.directory.manifest_path)
        if options.username or options.auth:
            options = get_credentials(options, target)
        env.target = Manifest(env.source.source(),
                              username=options.username,
                              password=options.password)
        env.update()

    elif command in ["remove", "deactivate", "activate"]:
        env.directory = Directory(target)
        env.source = Manifest(env.directory.manifest_path)
        getattr(env, command)()

    elif command == "environments":
        SPRINTER_ROOT = os.path.expanduser(os.path.join("~", ".sprinter"))
        for env in os.listdir(SPRINTER_ROOT):
            print "%s" % env

    elif command == "validate":
        if options.username or options.auth:
            options = get_credentials(parse_domain(target))
        errors = env.validate_manifest(target, username=options.username, password=options.password)
        if len(errors) > 0:
            print "Manifest is invalid!"
            print "\n".join(errors)
        else:
            print "Manifest is valid!"


def parse_domain(url):
    """ parse the domain from the url """
    domain_match = lib.DOMAIN_REGEX.match(url)
    if domain_match:
        return domain_match.group()


def get_credentials(options, environment):
    """ Get credentials or prompt for them from options """
    if options.username or options.auth:
        if not options.username:
            options.username = lib.prompt("Please enter the username for %s..." % environment)
        if not options.password:
            options.password = lib.prompt("Please enter the password for %s..." % environment, secret=True)
    return options

if __name__ == '__main__':
    main()
