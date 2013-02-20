"""
Generates a ssh key if necessary, and adds a config to ~/.ssh/config
if it doesn't exist already.
[ssh]
name = zillow
type = rsa
host = test.local
hostname = test
user = %(config:username)
"""

from sprinter.recipestandard import RecipeStandard


class SSHRecipe(RecipeStandard):

    def setup(self, feature_name, config):
        super(SSHRecipe, self).setup(feature_name, config)

    def update(self, feature_name, config):
        super(SSHRecipe, self).update(feature_name, config)

    def destroy(self, feature_name, config):
        super(SSHRecipe, self).destroy(feature_name, config)
