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

description = \
"""
Install an environment as specified in a sprinter config file
"""

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


def signal_handler(signal, frame):
    print "Shutting down sprinter..."
    sys.exit(0)


def main():
    signal.signal(signal.SIGINT, signal_handler)
    parse_args(sys.argv[1:])


def parse_args(argv, Environment=Environment):
    options, args = parser.parse_args(argv)
    command = args[0].lower()
    target = args[1]
    logging_level = logging.DEBUG if options.verbose else logging.INFO
    e = Environment(logging_level=logging_level)
    if command == "install":
        if options.username or options.auth:
            if not options.username:
                options.username = lib.prompt("Please enter the username for the sprinter url...")
            if not options.password:
                options.password = lib.prompt("Please enter the password for the sprinter url...", secret=True)
        e.install(target,
                  namespace=options.namespace,
                  username=options.username,
                  password=options.password)
    elif command == "update":
        if options.username or options.auth:
            if not options.username:
                options.username = lib.prompt("Please enter the username for the sprinter url...")
            if not options.password:
                options.password = lib.prompt("Please enter the password for the sprinter url...", secret=True)
        e.update(target, username=options.username, password=options.password)
    elif command == "remove":
        e.remove(target)
    elif command == "deactivate":
        e.deactivate(target)
    elif command == "activate":
        e.activate(target)
    elif command == "reload":
        e.reload(target)
    elif command == "environments":
        SPRINTER_ROOT = os.path.expanduser(os.path.join("~", ".sprinter"))
        for env in os.listdir(SPRINTER_ROOT):
            print "%s" % env

if __name__ == '__main__':
    main()
