"""
Creates a git repository and places it at the install location.
"""

import subprocess
import shutil

from sprinter.recipebase import RecipeBase


class GitRecipe(RecipeBase):
    """ A sprinter recipe for git"""

    def setup(self, feature_name, config):
        subprocess.call("git clone %s %s" % (config['url'], self.environment.install_directory(feature_name)))
        pass

    def update(self, feature_name, config):
        shutil.rmtree(self.environment.install_directory(feature_name))
        subprocess.call("git clone %s %s" % (config['target']['url'], self.environment.install_directory(feature_name)))
        pass

    def destroy(self, feature_name, old_config):
        shutil.rmtree(self.environment.install_directory(feature_name))
