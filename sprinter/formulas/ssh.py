"""
Generates a ssh key if necessary, and adds a config to ~/.ssh/config
if it doesn't exist already.
[github]
formula = sprinter.formulas.ssh
keyname = github
nopassphrase = true
type = rsa
hostname = github.com
user = toumorokoshi
"""
import os

from sprinter.formulastandard import FormulaStandard
from sprinter import lib

ssh_config_template = \
    """
Host %(keyname)s
  HostName %(hostname)s
  IdentityFile %(ssh_path)s
  User %(user)s
"""

ssh_config_path = os.path.expanduser('~/.ssh/config')


class SSHFormula(FormulaStandard):

    def setup(self, feature_name, config):
        ssh_path = self.__generate_key(feature_name, config)
        self.__install_ssh_config(config, ssh_path)
        if 'command' in config:
            self.__call_command(config['command'], ssh_path)

    def update(self, feature_name, config):
        ssh_path = self.__generate_key(feature_name, config['target'])
        self.__install_ssh_config(config['target'], ssh_path)
        if 'command' in config['target']:
            self.__call_command(config['target']['command'], ssh_path)

    def deactivate(self, feature_name, config):
        ssh_path = os.path.join(self.directory.install_directory(feature_name),
                                config['keyname'])
        self.__install_ssh_config(config, ssh_path)

    def activate(self, feature_name, config):
        ssh_path = os.path.join(self.directory.install_directory(feature_name),
                                config['keyname'])
        self.__install_ssh_config(config, ssh_path)

    def destroy(self, feature_name, config):
        super(SSHFormula, self).destroy(feature_name, config)

    def __generate_key(self, feature_name, config):
        """
        Generate the ssh key, and return the ssh config location
        """
        command = "ssh-keygen -t %(type)s -f %(keyname)s -N  " % config
        cwd = self.directory.install_directory(feature_name)
        if not os.path.exists(cwd):
            os.makedirs(cwd)
        if not os.path.exists(os.path.join(cwd, config['keyname'])):
            self.logger.info(lib.call(command, cwd=cwd))
        return os.path.join(cwd, config['keyname'])

    def __install_ssh_config(self, config, ssh_path):
        """
        Install the ssh configuration
        """
        config['ssh_path'] = ssh_path
        ssh_config_injection = ssh_config_template % config
        if os.path.exists(ssh_config_path):
            ssh_contents = open(ssh_config_path, "r+").read()
            if ssh_contents.find(config['host']) != -1 and \
                    not self.injections.injected(ssh_config_path):
                self.logger.info("SSH config for %s already exists! Override?")
                self.logger.info("Your existing config will not be overwritten, simply inactive.")
                overwrite = lib.prompt("Override?", boolean=True, default="no")
                if overwrite:
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
        self.logger.info(lib.call(command, bash=True))
