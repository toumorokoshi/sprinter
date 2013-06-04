"""
Generates a file in a target location from a template
[gitignore]
inputs = username
         password
formula = sprinter.formulas.template
source = http://mywebsite.com/.gitignore
target = ~/.gitignore
username = %(config:username)s
password = %(config:mywebsitepassword)s
"""
import os
import urllib

from sprinter.formulabase import FormulaBase


class TemplateFormula(FormulaBase):

    def install(self, feature_name, config):
        self.__install_file(config['source'], config['target'], config)
        super(TemplateFormula, self).install(feature_name, config)

    def update(self, feature_name, source_config, target_config):
        self.__install_file(target_config['source'], target_config['target'], target_config)
        super(TemplateFormula, self).update(feature_name, source_config, target_config)

    def remove(self, feature_name, config):
        super(TemplateFormula, self).remove(feature_name, config)

    def __install_file(self, source, target_file, config):
        source_content = None
        if source.startswith("http"):
            if 'username' in config and 'password' in config:
                source_content = self.lib.authenticated_get(config['username'],
                                                            config['password'],
                                                            source)
            else:
                source_content = urllib.urlopen(source).read()
        else:
            source_content = open(os.path.expanduser(source)).read()
        parent_directory = os.path.dirname(os.path.expanduser(target_file))
        if not os.path.exists(parent_directory):
            os.makedirs(parent_directory)
        open(os.path.expanduser(target_file), "w+").write(source_content)
