"""
Creates a git repository and places it at the install location.
"""
import os
import shutil

from sprinter.recipestandard import RecipeStandard
from sprinter.lib import call


class GitRecipe(RecipeStandard):
    """ A sprinter recipe for git"""

    def setup(self, feature_name, config):
        branch = (config['branch'] if 'branch' in config else None)
        self.__clone_repo(config['url'],
                          self.directory.install_directory(feature_name),
                          branch=branch)
        super(GitRecipe, self).setup(feature_name, config)

    def update(self, feature_name, config):
        target_directory = self.directory.install_directory(feature_name)
        source_branch = (config['source']['branch'] if 'branch' in config['source'] 
                         else "master")
        target_branch = (config['target']['branch'] if 'branch' in config['target'] 
                         else "master")
        if config['target']['url'] != config['source']['url'] or \
           not os.path.exists(target_directory):
            if os.path.exists(target_directory):
                self.logger.debug("Old git repository Found. Deleting...")
                shutil.rmtree(target_directory)
            self.__clone_repo(config['target']['url'],
                              target_directory,
                              branch=target_branch)
        elif source_branch != target_branch:
            self.__checkout_branch(target_directory, target_branch)
        else:
            if not os.path.exists(target_directory):
                self.logger.debug("No repository cloned. Re-cloning...")
                self.__clone_repo(config['target']['url'],
                                  target_directory,
                                  branch=target_branch)
            os.chdir(target_directory)
            error = call("git pull origin %s" % (config['target']['branch'] if 'branch' in config['target'] else 'master'))
            if error:
                self.logger.error("An error occured! Exiting...")
                return error
        super(GitRecipe, self).update(feature_name, config)

    def destroy(self, feature_name, config):
        super(GitRecipe, self).destroy(feature_name, config)
        shutil.rmtree(self.directory.install_directory(feature_name))

    def reload(self, feature_name, config):
        super(GitRecipe, self).reload(feature_name, config)
        os.chdir(self.directory.install_directory(feature_name))
        error = call("git pull origin %s" % (config['branch'] if 'branch' in config else 'master'))
        if error:
            self.logger.error("An error occured! Exiting...")
            return error

    def __checkout_branch(self, target_directory, branch):
        self.logger.debug("Checking out branch %s..." % branch)
        os.chdir(target_directory)
        error = call("git fetch origin %s" % branch)
        if error:
            self.logger.error("An error occured! Exiting...")
            return error
        error = call("git checkout %s" % branch)
        if error:
            self.logger.error("An error occured! Exiting...")
            return error

    def __clone_repo(self, repo_url, target_directory, branch=None):
        self.logger.debug("Cloning repository %s into %s..." % (repo_url, target_directory))
        error = call("git clone %s %s" % (repo_url, target_directory))
        if error:
            self.logger.error("An error occured! Exiting...")
            return error
        if branch:
            self.__checkout_branch(target_directory, branch)
