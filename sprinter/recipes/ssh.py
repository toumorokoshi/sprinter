"""
Generates a ssh key if necessary, and adds a config to ~/.ssh/config
if it doesn't exist already.
[github]
recipe = sprinter.recipe.ssh
keyname = github
nopassphrase = true
type = rsa
host = github.com
user = toumorokoshi
"""
import os

from sprinter.recipestandard import RecipeStandard

ssh_config_template = \
"""
Host %(hostname)
  HostName
  IdentityFile %(ssh_path)
  User %(user)
"""


class SSHRecipe(RecipeStandard):

    def setup(self, feature_name, config):
        super(SSHRecipe, self).setup(feature_name, config)
        ssh_path = self.__generate_key(feature_name, config)
        self.__install_ssh_config(config, ssh_path)

    def update(self, feature_name, config):
        super(SSHRecipe, self).update(feature_name, config)
        ssh_path = self.__generate_key(feature_name, config)
        self.__install_ssh_config(config)

    def destroy(self, feature_name, config):
        super(SSHRecipe, self).destroy(feature_name, config)

    def __generate_key(feature_name, config):
        """
        Generate the ssh key, and return the ssh config location
        """
        passphrase = "" if config['nopassphrase'] else config['passphrase']
        command = "ssh-keygen -t %(type)s -N '' -f %(keyname)s"
        cwd = self.directory.install_directory(feature_name)
        if not os.path.exists(cwd, config['keyname']):
          lib.call(command, cwd=cwd)
        return os.path.join(cwd, config['keyname'])

    def __install_ssh_config(self, config, ssh_path):
        """
        Install the ssh configuration
        """        
        config['ssh_path'] = ssh_path
        ssh_config_injection = ssh_config_template % config
        self.injections.inject(os.path.expanduser("~/.ssh/config"), ssh_config_injection)
