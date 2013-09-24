"""Sprinter, an environment installation and management tool.
Usage:
  sprinter install <environment_source> [-av -n <namespace> -u <username> -p <password> --allow-bad-certificate]
  sprinter update <environment_name> [-rav -u <username> -p <password> --allow-bad-certificate]
  sprinter (remove | deactivate | activate) <environment_name> [-v]
  sprinter validate <environment_source> [-av -u <username> -p <password> --allow-bad-certificate]
  sprinter environments
  sprinter (-h | --help)

Options:
  -h, --help                                Show this usage guide.
  -v, --verbose                             Sprinter output is verbose
  -n <namespace>, --namespace <namespace>   Explicitely specify a namespace to name the environment, on install
  -r, --reconfigure                         During an update, ask the user again for customization parameters
  -a, --auth                                When pulling environment configurations, attempt basic authentication
  -u <username>, --username <username>      When using basic authentication, this is the username used
  -p <password>, --password <password>      When using basic authentication, this is the password used
  --allow-bad-certificate                   Do not verify ssl certificates when pulling environment configurations
"""

import logging
import os
import signal
import sys
from docopt import docopt

import sprinter.lib as lib
from sprinter.core import PHASE
from sprinter.environment import Environment
from sprinter.manifest import Manifest, ManifestException
from sprinter.directory import Directory
from sprinter.exceptions import SprinterException, BadCredentialsException


def signal_handler(signal, frame):
    print("\nShutting down sprinter...")
    sys.exit(0)


def main():
    signal.signal(signal.SIGINT, signal_handler)
    try:
        parse_args(sys.argv[1:])
    except SprinterException:
        e = sys.exc_info()[1]
        print(str(e))
        print("Sprinter shut down with an error!")
    except BadCredentialsException:
        e = sys.exc_info()[1]
        print(str(e))
        print("Invalid username and password combination!")


def error(message):
    print(message)
    exit()


def parse_args(argv, Environment=Environment):
    options = docopt(__doc__, argv=argv, version="Sprinter 1.0")
    logging_level = logging.DEBUG if options['--verbose'] else logging.INFO
    # start processing commands
    env = Environment(logging_level=logging_level)
    try:
        if options['install']:
            target = options['<environment_source>']

            def handle_install_shutdown(signal, frame):
                if env.phase == PHASE.INSTALL:
                    print("Removing install...")
                    env.directory.remove()
                    env.clear_all()
                signal_handler(signal, frame)
            signal.signal(signal.SIGINT, handle_install_shutdown)
            if options['--username'] or options['--auth']:
                options = get_credentials(options, parse_domain(target))
                target = Manifest(target,
                                  username=options['<username>'],
                                  password=options['<password>'],
                                  verify_certificate=(not options['--allow-bad-certificate']))
            env.target = target
            if options['--namespace']:
                env.namespace = options['<namespace>']
            env.install()

        elif options['update']:
            target = options['<environment_name>']
            env.directory = Directory(target,
                                      sprinter_root=env.root,
                                      shell_util_path=env.shell_util_path)
            env.source = Manifest(env.directory.manifest_path)
            use_auth = options['--username'] or options['--auth']
            if use_auth:
                options = get_credentials(options, target)
            env.target = Manifest(env.source.source(),
                                  username=options['<username>'] if use_auth else None,
                                  password=options['<password>'] if use_auth else None,
                                  verify_certificate=(not options['--allow-bad-certificate']))
            env.update(reconfigure=options['--reconfigure'])

        elif options["remove"]:
            env.directory = Directory(options['<environment_name>'],
                                      sprinter_root=env.root,
                                      shell_util_path=env.shell_util_path)
            env.source = Manifest(env.directory.manifest_path, namespace=options['<environment_name>'])
            env.remove()

        elif options['deactivate']:
            env.directory = Directory(options['<environment_name>'],
                                      sprinter_root=env.root,
                                      shell_util_path=env.shell_util_path)
            env.source = Manifest(env.directory.manifest_path, namespace=options['<environment_name>'])
            env.deactivate()

        elif options['activate']:
            env.directory = Directory(options['<environment_name>'],
                                      sprinter_root=env.root,
                                      shell_util_path=env.shell_util_path)
            env.source = Manifest(env.directory.manifest_path, namespace=options['<environment_name>'])
            env.activate()

        elif options['environments']:
            SPRINTER_ROOT = os.path.expanduser(os.path.join("~", ".sprinter"))
            for env in os.listdir(SPRINTER_ROOT):
                if env != ".global":
                    print(env)

        elif options['validate']:
            if options['--username'] or options['--auth']:
                options = get_credentials(options, parse_domain(target))
                target = Manifest(options['<environment_source>'],
                                  username=options['<username>'],
                                  password=options['<password>'],
                                  verify_certificate=(not options['--allow-bad-certificate']))
            env.target = options['<environment_source>']
            env.validate()
            if not env.error_occured:
                print("No errors! Manifest is valid!")
            else:
                "Manifest is invalid! Please see errors above."
    except BadCredentialsException:
        e = sys.exc_info()[1]
        raise e
    except ManifestException:
        e = sys.exc_info()[1]
        print(str(e))
        print("Could not find Manifest!")
    except Exception:
        e = sys.exc_info()[1]
        env.log_error(str(e))
        env.logger.info("failed! Writing debug output to /tmp/sprinter.log")
        env.write_debug_log("/tmp/sprinter.log")
        if env.message_failure():
            env.logger.info(env.message_failure())


def parse_domain(url):
    """ parse the domain from the url """
    domain_match = lib.DOMAIN_REGEX.match(url)
    if domain_match:
        return domain_match.group()


def get_credentials(options, environment):
    """ Get credentials or prompt for them from options """
    if options['--username'] or options['--auth']:
        if not options['--username']:
            options['<username>'] = lib.prompt("Please enter the username for %s..." % environment)
        if not options['--password']:
            options['<password>'] = lib.prompt("Please enter the password for %s..." % environment, secret=True)
    return options

if __name__ == '__main__':
    main()
