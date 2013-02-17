"""
Installs a package from whatever the native package manager is
(apt-get for debian-based, brew for OS X)
"""

from sprinter.recipebase import RecipeBase


class PackageRecipe(RecipeBase):

    def __init__(self, environment):
        super(PackageRecipe, self).__init__(environment)
        self.package_manager = self.__get_package_manager()

    def setup(self, feature_name, config):
        pass

    def update(self, feature_name, config):
        pass

    def destroy(self, feature_name, config):
        pass

    def __get_package_manager():
        if self.environment.isOSX():
            return "brew"
        elif self.environment.isDebianBased():
            return "apt-get"
        elif self.environment.isFedoraBased():
            return "yum"
