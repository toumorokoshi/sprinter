"""
Generates a ssh key if necessary, and adds a config to ~/.ssh/config
if it doesn't exist already.
[github]
formula = sprinter.formula.ssh
keyname = github
nopassphrase = true
type = rsa
hostname = github.com
user = toumorokoshi
create = false
install_command = echo 'hello'
"""
from __future__ import unicode_literals
import os
import logging

from sprinter.formula.base import FormulaBase
from sprinter.core import PHASE
import sprinter.lib as lib

ssh_config_template = """
Host %(host)s
  HostName %(hostname)s
  IdentityFile %(ssh_key_path)s
  User %(user)s
"""

user_ssh_path = os.path.expanduser("~/.ssh")
ssh_config_path = os.path.join(user_ssh_path, "config")


class SSHFormula(FormulaBase):

    required_options = FormulaBase.required_options + ['keyname', 'hostname',
                                                       'user', 'host']
    valid_options = FormulaBase.valid_options + ['override', 'install_command',
                                                 'create', 'nopassphrase',
                                                 'type', 'ssh_path',
                                                 'use_global_ssh', 'port']

    def prompt(self):
        if self.environment.phase in (PHASE.INSTALL, PHASE.UPDATE):
            if os.path.exists(ssh_config_path):
                self._prompt_value('use_global_ssh',
                                   "Would you like to manage your own ssh configuration?",
                                   default="no")

    def install(self):
        self.__generate_key(self.target)
        self.__install_ssh_config(self.target)
        if self.target.has('install_command'):
            self.__call_command(self.target.get('install_command'), self.target.get('ssh_key_path'))

    def update(self):
        self.__generate_key(self.target)
        self.__install_ssh_config(self.target)

    def deactivate(self):
        self.injections.inject(ssh_config_path, "")

    def remove(self):
        self.injections.inject(ssh_config_path, "")

    def activate(self):
        self.__install_ssh_config(self.source)

    def __generate_key(self, config):
        """
        Generate the ssh key, and return the ssh config location
        """
        cwd = config.get('ssh_path', self.directory.install_directory(self.feature_name))
        if not config.has('create') or config.is_affirmative('create'):
            if not os.path.exists(cwd):
                os.makedirs(cwd)
            if not os.path.exists(os.path.join(cwd, config.get('keyname'))):
                command = "ssh-keygen -t %(type)s -f %(keyname)s -N  " % config.to_dict()
                lib.call(command, cwd=cwd, output_log_level=logging.DEBUG)
        if not config.has('ssh_path'):
            config.set('ssh_path', cwd)
        config.set('ssh_key_path', os.path.join(config.get('ssh_path'), config.get('keyname')))

    def __install_ssh_config(self, config):
        """
        Install the ssh configuration
        """
        if not config.is_affirmative('use_global_ssh', default="no"):
            ssh_config_injection = self._build_ssh_config(config)

            if not os.path.exists(ssh_config_path):

                if self.injections.in_noninjected_file(ssh_config_path, "Host %s" % config.get('host')):
                    if config.is_affirmative('override'):
                        self.injections.inject(ssh_config_path, ssh_config_injection)
                else:
                    self.injections.inject(ssh_config_path, ssh_config_injection)

            else:
                self.injections.inject(ssh_config_path, ssh_config_injection)

            self.injections.commit()

    def __call_command(self, command, ssh_path):
        ssh_path += ".pub"  # make this the public key
        ssh_contents = open(ssh_path, 'r').read().rstrip('\n')
        command = command.replace('{{ssh}}', ssh_contents)
        lib.call(command, shell=True, output_log_level=logging.DEBUG)

    def _build_ssh_config(self, config):
        """ build the ssh injection configuration """
        ssh_config_injection = ssh_config_template % {
            'host': config.get('host'),
            'hostname': config.get('hostname'),
            'ssh_key_path': config.get('ssh_key_path'),
            'user': config.get('user')
        }
        if config.has('port'):
            ssh_config_injection += "  Port {0}\n".format(config.get('port'))
        return ssh_config_injection
