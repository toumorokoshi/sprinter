"""
Queries the user for a specific environment

[env]
recipe = sprinter.recipes.env
stash = %(config:stash)
user = %(config:user)
MAVEN_HOME = %(maven:root_dir)
M2_PATH = ~/.m2/
"""
from sprinter.recipestandard import RecipeStandard


class EnvRecipe(RecipeStandard):
    """ A sprinter recipe for git"""

    def setup(self, feature_name, config):
        super(EnvRecipe, self).setup(feature_name, config)
        [self.directory.add_to_rc('export %s=%s' % (c.upper(), config[c])) \
             for c in config if c != 'recipe']

    def update(self, feature_name, config):
        super(EnvRecipe, self).update(feature_name, config)
        [self.directory.add_to_rc('export %s=%s' % (c.upper(), config['target'][c])) \
             for c in config['target'] if c != 'recipe']

    def destroy(self, feature_name, config):
        super(EnvRecipe, self).destroy(feature_name, config)
        pass
