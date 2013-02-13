"""
Installs a package from whatever the native package manager is
(apt-get for debian-based, brew for OS X)
"""

from sprinter.recipebase import RecipeBase


class PackageRecipe(RecipeBase):

    def setup(self, config):
        pass

    def update(self, config):
        pass

    def destroy(self, config):
        pass
