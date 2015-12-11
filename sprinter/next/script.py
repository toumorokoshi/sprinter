"""Sprinter, an environment installation and management tool.
Usage:
  sprinter install <package_source> [-v]
  sprinter update <package_name> [-rv]
  sprinter (remove | deactivate | activate) <package_name> [-v]
  sprinter validate <package_source> [-v]
  sprinter packages
  sprinter globals [-r]
  sprinter (-h | --help)
  sprinter (-V | --version)

Options:
  -h, --help          show this usage guide.
  -v, --verbose       sprinter output is verbose
  -r, --reconfigure   ask the user for customization parameters
  -V, --version       show version.
"""
from __future__ import unicode_literals
import docopt
import logging
import pprint
import os
import signal
import sys
from .sprinter import Sprinter

LOGGING_NAMES = ["sprinter"]
VALID_COMMANDS = [
    "install", "update", "validate", "remove", "deactivate", "activate"
]
CONSUMED_BY_SCRIPT = ["--verbose", "--version"]
PRINTER = pprint.PrettyPrinter(indent=4)


def main(argv=sys.argv[1:]):
    signal.signal(signal.SIGINT, _signal_handler)
    try:
        _run(argv)
    except:
        e = sys.exc_info()[1]
        print(str(e))
        print("Sprinter shut down with an error!")


def _run(argv):
    options = docopt.docopt(__doc__,  argv=argv, options_first=True)
    logging_level = logging.DEBUG if options["--verbose"] else logging.INFO
    _create_stdout_logger(logging_level)
    home_directory = os.path.expanduser("~")
    sprinter = Sprinter(home_directory)
    kwargs = dict((k,v) for k,v in options.items() if k not in CONSUMED_BY_SCRIPT)
    for command in VALID_COMMANDS:
        if options[command]:
            PRINTER.pprint(getattr(sprinter, command)(**kwargs))


def _signal_handler(signal, frame):
    print("\nShutting down sprinter...")
    sys.exit(0)


def _create_stdout_logger(logging_level):
    """
    create a logger to stdout. This creates logger for a series
    of module we would like to log information on.
    """
    out_hdlr = logging.StreamHandler(sys.stdout)
    out_hdlr.setFormatter(logging.Formatter(
        '[%(asctime)s] %(message)s', "%H:%M:%S"
    ))
    out_hdlr.setLevel(logging_level)
    for name in LOGGING_NAMES:
        log = logging.getLogger(name)
        log.addHandler(out_hdlr)
        log.setLevel(logging_level)
