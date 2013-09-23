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
on_update = false
"""
import os
import requests

from sprinter.formulabase import FormulaBase
from sprinter.core import PHASE


class TemplateFormula(FormulaBase):

    required_options = FormulaBase.required_options + ['source', 'target']

    def prompt(self):
        if self.environment.phase == PHASE.REMOVE:
            self.source.prompt('remove_file_on_delete',
                               "Would you like to remove %s?" % self.source.get('target'),
                               default="yes")

    def install(self):
        self.__install_file(self.target)
        FormulaBase.install(self)

    def update(self):
        if self.target.has('on_update') and self.target.is_affirmative('on_update'):
            self.__install_file(self.target)
        FormulaBase.update(self)

    def remove(self):
        if self.source.is_affirmative('remove_file_on_delete', False):
            os.path.unlink(
                os.path.expanduser(self.source.get('target')))
        FormulaBase.remove(self)

    def validate(self):
        if self.target:
            if (self.target.has('username') and not self.target.has('password') or
               self.target.has('password') and not self.target.has('username')):
                self.logger.warn("Username and password are " +
                                 "both required to authenticate to a source!")
        FormulaBase.validate(self)

    def __install_file(self, config):
        source = config.get('source')
        if source.startswith("http"):
            if config.has('username') and config.has('password'):
                source_content = self.lib.authenticated_get(config.get('username'),
                                                            config.get('password'),
                                                            source).decode("utf-8")
            else:
                source_content = requests.get(source).text
        else:
            source_content = open(os.path.expanduser(source)).read()
        target_file = os.path.expanduser(config.get('target'))
        parent_directory = os.path.dirname(target_file)
        if not os.path.exists(parent_directory):
            os.makedirs(parent_directory)
        with open(target_file, 'w+') as fh:
            fh.write(source_content)
