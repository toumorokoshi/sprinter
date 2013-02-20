"""
Runs a command
[ssh]
command = cd ~/.ssh/ && ssh-keygen -f 'zillow' -t rsa -P
"""

from sprinter.recipestandard import RecipeStandard


class CommandRecipe(RecipeStandard):

    def setup(self, feature_name, config):
        super(CommandRecipe, self).setup(feature_name, config)

    def update(self, feature_name, config):
        super(CommandRecipe, self).update(feature_name, config)

    def destroy(self, feature_name, config):
        super(CommandRecipe, self).destroy(feature_name, config)
