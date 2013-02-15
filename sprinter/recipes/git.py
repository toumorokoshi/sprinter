"""
Unpacks and deploys to a location
"""

import gzip
import os
import tarfile
import urllib
from StringIO import StringIO

from sprinter.recipebase import RecipeBase


class GitRecipe(RecipeBase):
    """ A sprinter recipe for git"""

    def setup(self, directory, feature_name, config):
        pass

    def update(self, directory, feature_name, old_config):
        pass

    def destroy(self, directory, feature_name, old_config):
        pass
