"""
Generates a ssh key if necessary, and adds a config to ~/.ssh/config
if it doesn't exist already.
[github]
recipe = sprinter.recipe.ssh
keyname = github
nopassphrase = true
type = rsa
hostname = github.com
user = toumorokoshi
"""
import os
import urllib2

from sprinter.recipestandard import RecipeStandard
from sprinter import lib

ssh_config_template = \
"""
Host %(keyname)s
  HostName %(hostname)s
  IdentityFile %(ssh_path)s
  User %(user)s
"""


class SSHRecipe(RecipeStandard):

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

    def destroy(self, feature_name, config):
        super(SSHRecipe, self).destroy(feature_name, config)

    def __generate_key(self, feature_name, config):
        """
        Generate the ssh key, and return the ssh config location
        """
        passphrase = "" if config['nopassphrase'] else config['passphrase']
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
        self.injections.inject(os.path.expanduser("~/.ssh/config"), ssh_config_injection)
        self.injections.commit()

    def __call_command(self, command, ssh_path):
        ssh_path += ".pub"  # make this the public key
        ssh_contents = open(ssh_path, 'r').read().rstrip('\n')
        command = command.replace('{{ssh}}', ssh_contents)
        self.logger.info(lib.call(command, bash=True))
