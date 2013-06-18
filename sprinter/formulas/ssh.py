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
ssh_path = 
create = false
"""
import os
import re

from sprinter.formulabase import FormulaBase

ssh_config_template = \
    """
Host %(host)s
  HostName %(hostname)s
  IdentityFile %(ssh_path)s
  User %(user)s
"""

ssh_config_path = os.path.expanduser('~/.ssh/config')


class SSHFormula(FormulaBase):

    def install(self, feature_name, config):
        ssh_path = self.__generate_key(feature_name, config)
        self.__install_ssh_config(config, ssh_path)
        if 'command' in config:
            self.__call_command(config['command'], ssh_path)

    def update(self, feature_name, source_config, target_config):
        ssh_path = self.__generate_key(feature_name, target_config)
        self.__install_ssh_config(target_config, ssh_path)
        #super(SSHFormula, self).update(feature_name, source_config, target_config)

    def remove(self, feature_name, config):
        super(SSHFormula, self).remove(feature_name, config)

    def deactivate(self, feature_name, config):
        ssh_path = os.path.join(self.directory.install_directory(feature_name),
                                config['keyname'])
        self.__install_ssh_config(config, ssh_path)
        #super(SSHFormula, self).deactivate(feature_name, config)

    def activate(self, feature_name, config):
        ssh_path = os.path.join(self.directory.install_directory(feature_name),
                                config['keyname'])
        self.__install_ssh_config(config, ssh_path)
        #super(SSHFormula, self).activate(feature_name, config)

    def __generate_key(self, feature_name, config):
        """
        Generate the ssh key, and return the ssh config location
        """
        command = "ssh-keygen -t %(type)s -f %(keyname)s -N  " % config
        cwd = self.directory.install_directory(feature_name)
        if 'ssh_path' in config:
            cwd = config['ssh_path']
        if 'create' not in config or config['create'].lower().startswith('t'):
            if not os.path.exists(cwd):
                os.makedirs(cwd)
            if not os.path.exists(os.path.join(cwd, config['keyname'])):
                self.logger.info(self.lib.call(command, cwd=cwd))
        return os.path.join(cwd, config['keyname'])

    def __install_ssh_config(self, config, ssh_path):
        """
        Install the ssh configuration
        """
        config['ssh_path'] = ssh_path
        ssh_config_injection = ssh_config_template % config
        if os.path.exists(ssh_config_path):
            if self.injections.in_noninjected_file(ssh_config_path, "Host %s" % config['host']):
                self.logger.info("SSH config for host %s already exists! Override?" % config['host'])
                self.logger.info("Your existing config will not be overwritten, simply inactive.")
                overwrite = self.lib.prompt("Override?", boolean=True, default="no")
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
        self.logger.info(self.lib.call(command, bash=True))
