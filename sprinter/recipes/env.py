"""
Queries the user for a specific environment

[env]
recipe = sprinter.recipes.env
stash = %(config:stash)
_default_stash = ~/stash
user = %(config:user)
"""
import os
import shutil

from sprinter.recipestandard import RecipeStandard
from sprinter.lib import call


class EnvRecipe(RecipeStandard):
    """ A sprinter recipe for git"""

    def setup(self, feature_name, config):
        super(EnvRecipe, self).setup(feature_name, config)
        for c in config:
            if c != 'recipe' and not c.startswith("_default"):
                #self.environment.add_to_rc("export %s=%s" % (c
                pass

    def update(self, feature_name, config):
        super(EnvRecipe, self).update(feature_name, config)
        pass

    def destroy(self, feature_name, config):
        super(EnvRecipe, self).destroy(feature_name, config)
        pass

    def reload(self, feature_name, config):
        super(EnvRecipe, self).reload(feature_name, config)
        pass
