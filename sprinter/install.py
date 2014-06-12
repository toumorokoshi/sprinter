"""Sprinter, an environment installation and management tool.
Usage:
  sprinter install <environment_source> [-avi -n <namespace> -u <username> -p <password> -l <local_path> --allow-bad-certificate]
  sprinter update <environment_name> [-ravi -u <username> -p <password> --allow-bad-certificate]
  sprinter (remove | deactivate | activate) <environment_name> [-v]
  sprinter validate <environment_source> [-avi -u <username> -p <password> --allow-bad-certificate]
  sprinter environments
  sprinter globals [-r]
  sprinter (-h | --help)
  sprinter (-V | --version)

Options:
  -h, --help                                Show this usage guide.
  -v, --verbose                             Sprinter output is verbose
  -n <namespace>, --namespace <namespace>   Explicitely specify a namespace to name the environment, on install
  -r, --reconfigure                         During an update, ask the user again for customization parameters
  -a, --auth                                When pulling environment configurations, attempt basic authentication
  -u <username>, --username <username>      When using basic authentication, this is the username used
  -p <password>, --password <password>      When using basic authentication, this is the password used
  -l, --local <local_path>                  Intall the environment as a local. This installs objects relative to the local directory, and doesn't inject.
  -i, --ignore-errors                       Ignore errors in a formula
  --allow-bad-certificate                   Do not verify ssl certificates when pulling environment configurations
  -V, --version                             Show version.
"""
from __future__ import unicode_literals
import logging
import os
import signal
import sys
import pkg_resources
from docopt import docopt

import sprinter.lib as lib
from sprinter.core import PHASE, Manifest, ManifestException, Directory, manifest
from sprinter.environment import Environment
from sprinter.exceptions import SprinterException
from sprinter.lib.request import BadCredentialsException
from sprinter.core.globals import print_global_config, configure_config, write_config

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
    options = docopt(__doc__, argv=argv, version= pkg_resources.get_distribution('sprinter').version)
    logging_level = logging.DEBUG if options['--verbose'] else logging.INFO
    # start processing commands
    env = Environment(logging_level=logging_level, ignore_errors=options['--ignore-errors'])
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
                target = manifest.load_manifest(
                    target,
                    username=options['<username>'],
                    password=options['<password>'],
                    verify_certificate=(not options['--allow-bad-certificate'])
                )
            else:
                target = manifest.load_manifest(
                    target,
                    verify_certificate=(not options['--allow-bad-certificate'])
                )
            env.target = target
            if options['--namespace']:
                env.namespace = options['<namespace>']
            if options['--local']:
                env.do_inject_environment_config = False
                env.custom_directory_root = os.path.abspath(os.path.expanduser(options['--local']))
            env.install()

        elif options['update']:
            target = options['<environment_name>']
            env.directory = Directory(os.path.join(env.root, target),
                                      shell_util_path=env.shell_util_path)
            env.source = manifest.load_manifest(
                env.directory.manifest_path, do_inherit=False
            )
            use_auth = options['--username'] or options['--auth']
            if use_auth:
                options = get_credentials(options, target)
            env.target = manifest.load_manifest(
                env.source.source(),
                username=options['<username>'] if use_auth else None,
                password=options['<password>'] if use_auth else None,
                verify_certificate=(not options['--allow-bad-certificate'])
            )
            env.update(reconfigure=options['--reconfigure'])

        elif options["remove"]:
            env.directory = Directory(os.path.join(env.root, options['<environment_name>']),
                                      shell_util_path=env.shell_util_path)
            env.source = manifest.load_manifest(
                env.directory.manifest_path,
                namespace=options['<environment_name>'],
                do_inherit=False
            )
            env.remove()

        elif options['deactivate']:
            env.directory = Directory(os.path.join(env.root, options['<environment_name>']),
                                      shell_util_path=env.shell_util_path)
            env.source = manifest.load_manifest(
                env.directory.manifest_path,
                namespace=options['<environment_name>'],
                do_inherit=False
            )
            env.deactivate()

        elif options['activate']:
            env.directory = Directory(os.path.join(env.root, options['<environment_name>']),
                                      shell_util_path=env.shell_util_path)
            env.source = manifest.load_manifest(
                env.directory.manifest_path,
                namespace=options['<environment_name>'],
                do_inherit=False
            )
            env.activate()

        elif options['environments']:
            SPRINTER_ROOT = os.path.expanduser(os.path.join("~", ".sprinter"))
            for env in os.listdir(SPRINTER_ROOT):
                if env != ".global":
                    print(env)

        elif options['validate']:
            if options['--username'] or options['--auth']:
                options = get_credentials(options, parse_domain(target))
                target = manifest.load_manifest(
                    options['<environment_source>'],
                    username=options['<username>'],
                    password=options['<password>'],
                    verify_certificate=(not options['--allow-bad-certificate'])
                )
            env.target = options['<environment_source>']
            env.validate()
            if not env.error_occured:
                print("No errors! Manifest is valid!")
            else:
                "Manifest is invalid! Please see errors above."
        elif options['globals']:
            if options['--reconfigure']:
                configure_config(env.global_config, reconfigure=True)
                write_config(env.global_config, env.global_config_path)
            else:
                print_global_config(env.global_config)
    except BadCredentialsException:
        e = sys.exc_info()[1]
        raise e
    except ManifestException:
        e = sys.exc_info()[1]
        env.log_error(str(e))
        env.logger.info("Error occured when attempting to load manifest!")
        env.logger.info("Writing debug output to /tmp/sprinter.log")
        env.write_debug_log("/tmp/sprinter.log")
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
