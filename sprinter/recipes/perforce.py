"""
Creates a git repository and places it at the install location.

[perforce]
recipe = sprinter.recipes.perforce
version = r10.1
default_path = ~/p4/
"""
import os
import shutil
import urllib

from sprinter.recipestandard import RecipeStandard
from sprinter.lib import call

url_template = "http://filehost.perforce.com/perforce/%s/%s/p4"
exec_dict = {"r10.1": {"mac": "bin.macosx104u",
                       "linux": "bin.linux26x86_64"}}


class PerforceRecipe(RecipeStandard):
    """ A sprinter recipe for git"""

    def setup(self, feature_name, config):
        super(PerforceRecipe, self).setup(feature_name, config)
        self.__install_perforce(feature_name, config)

    def update(self, feature_name, config):
        if config['source']['version'] != config['target']['version']:
            os.remove(os.path.join(self.environment.install_directory(feature_name), 'p4'))
            self.__install_perforce(self, feature_name, config['target'])

    def destroy(self, feature_name, config):
        pass

    def reload(self, feature_name, config):
        pass

    def __install_perforce(self, feature_name, config):
        exec_dir = exec_dict[config['version']]['mac'] if self.environment.isOSX() else \
            exec_dict[config['version']]['linux']
        url = url_template % (config['version'], exec_dir)
        d = self.environment.install_directory(feature_name)
        os.makedirs(d)
        self.logger.info("Downloading p4 executable...")
        urllib.urlretrieve(url, os.path.join(d, "p4"))
        self.environment.symlink_to_bin("p4", os.path.join(d, "p4"))

    def __sync_perforce(self, feature_name, config):
        pass
