"""
Creates a git repository and places it at the install location.
"""
import os
import shutil

from sprinter.recipebase import RecipeBase
from sprinter.lib import call


class GitRecipe(RecipeBase):
    """ A sprinter recipe for git"""

    def setup(self, feature_name, config):
        super(GitRecipe, self).setup(feature_name, config)
        branch = (config['branch'] if 'branch' in config else None)
        self.__clone_repo(config['url'], self.environment.install_directory(feature_name), branch=branch)

    def update(self, feature_name, config):
        super(GitRecipe, self).update(feature_name, config)
        shutil.rmtree(self.environment.install_directory(feature_name))
        branch = (config['branch'] if 'branch' in config else None)
        self.__clone_repo(config['target']['url'], self.environment.install_directory(feature_name),
                          branch=branch)

    def destroy(self, feature_name, config):
        super(GitRecipe, self).destroy(feature_name, config)
        shutil.rmtree(self.environment.install_directory(feature_name))

    def __clone_repo(self, repo_url, target_directory, branch=None):
        call("git clone %s %s" % (repo_url, target_directory))
        if branch:
            os.chdir(target_directory)
            call("git fetch origin %s" % branch)
            call("git checkout %s" % branch)
