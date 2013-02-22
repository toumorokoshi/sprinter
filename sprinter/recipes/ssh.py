"""
Generates a ssh key if necessary, and adds a config to ~/.ssh/config
if it doesn't exist already.
[ssh]
recipe = sprinter.recipes.ssh
name = zillow
type = rsa
host = test.local
hostname = test
user = %(config:username)
"""

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
        self.__generate_key(feature_name)
        self.__install_ssh_config(config)

    def update(self, feature_name, config):
        super(SSHRecipe, self).update(feature_name, config)
        self.__install_ssh_config(config)

    def destroy(self, feature_name, config):
        super(SSHRecipe, self).destroy(feature_name, config)
