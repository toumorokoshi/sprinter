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
import os
import logging

from sprinter.formulabase import FormulaBase
from sprinter.core import PHASE
from sprinter import lib

ssh_config_template = """
Host %(host)s
  HostName %(hostname)s
  IdentityFile %(ssh_key_path)s
  User %(user)s
"""

ssh_config_path = os.path.expanduser('~/.ssh/config')


class SSHFormula(FormulaBase):

    required_options = FormulaBase.required_options + ['keyname', 'hostname', 'user', 'host']
    valid_options = FormulaBase.valid_options + ['override', 'install_command', 'create',
                                                 'nopassphrase', 'type', 'ssh_path']

    def prompt(self, reconfigure=False):
        if self.environment.phase in (PHASE.INSTALL, PHASE.UPDATE):
            if os.path.exists(ssh_config_path):
                if (self.injections.in_noninjected_file(
                        ssh_config_path, "Host %s" % self.target.get('host')) and
                   not self.target.has('override')):
                    self.logger.info("SSH config for host %s already exists! Override?" %
                                     self.target.get('host'))
                    self.logger.info("Your existing config will not be overwritten, simply inactive.")
                    self.target.set('override', lib.prompt("Override?", boolean=True, default="no"))

    def install(self):
        ssh_key_path = self.__generate_key(self.target)
        self.__install_ssh_config(self.target, ssh_key_path)
        if self.target.has('install_command'):
            self.__call_command(self.target.get('install_command'), ssh_key_path)

    def update(self):
        ssh_key_path = self.__generate_key(self.target)
        self.__install_ssh_config(self.target, ssh_key_path)

    def deactivate(self):
        ssh_key_path = os.path.join(self.directory.install_directory(self.feature_name),
                                    self.source.get('keyname'))
        self.__install_ssh_config(self.source, ssh_key_path)

    def remove(self):
        self.injections.inject(ssh_config_path, "")

    def activate(self):
        ssh_key_path = os.path.join(self.directory.install_directory(self.feature_name),
                                    self.source.get('keyname'))
        self.__install_ssh_config(self.source, ssh_key_path)

    def __generate_key(self, config):
        """
        Generate the ssh key, and return the ssh config location
        """
        command = "ssh-keygen -t %(type)s -f %(keyname)s -N  " % config.to_dict()
        cwd = config.get('ssh_path', self.directory.install_directory(self.feature_name))
        if not config.has('create') or config.is_affirmative('create'):
            if not os.path.exists(cwd):
                os.makedirs(cwd)
            if not os.path.exists(os.path.join(cwd, config.get('keyname'))):
                lib.call(command, cwd=cwd, output_log_level=logging.DEBUG)
        if not config.has('ssh_path'):
            config.set('ssh_path', cwd)
        return os.path.join(cwd, config.get('keyname'))

    def __install_ssh_config(self, config, ssh_key_path):
        """
        Install the ssh configuration
        """
        config.set('ssh_key_path', ssh_key_path)
        ssh_config_injection = ssh_config_template % config.to_dict()
        if os.path.exists(ssh_config_path):
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
