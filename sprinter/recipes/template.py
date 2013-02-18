"""
Generates a file in a target location from a template
"""
import os
import urllib

from sprinter.recipestandard import RecipeStandard


class TemplateRecipe(RecipeStandard):

    def setup(self, feature_name, config):
        super(TemplateRecipe, self).setup(feature_name, config)
        self.__install_file(config['source'], config['target'])

    def update(self, feature_name, config):
        super(TemplateRecipe, self).update(feature_name, config)
        self.__install_file(config['source'], config['target'])

    def destroy(self, feature_name, config):
        super(TemplateRecipe, self).destroy(feature_name, config)
        pass

    def __install_file(self, source, target_file):
        source_content = (urllib.urlopen(source) if source.startswith("http") else
                          open(os.path.expanduser(source))).read()
        open(os.path.expanduser(target_file), "w+").write(source_content)
