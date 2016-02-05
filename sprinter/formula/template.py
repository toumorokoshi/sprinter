"""
Generates a file in a target location from a template
[gitignore]
inputs = username
         password
         my_tmpl_var==default value
         other_tmpl_var==develop
formula = sprinter.formula.template
source = http://mywebsite.com/.gitignore
target = ~/.gitignore
username = %(config:username)s
password = %(config:mywebsitepassword)s
replacement_keys = my_tmpl_var,other_tmpl_var
my_tmpl_var = %(config:my_tmpl_var)s
other_tmpl_var = %(config:other_tmpl_var)s
on_update = false
"""
from __future__ import unicode_literals
import os
import string

from collections import defaultdict

from sprinter.formula.base import FormulaBase
import sprinter.lib as lib
from sprinter.core import PHASE


class TemplateFormula(FormulaBase):

    required_options = FormulaBase.required_options + ['source', 'target']
    valid_options = ['fail_on_error']

    def prompt(self):
        if self.environment.phase == PHASE.REMOVE:
            self.source.prompt('remove_file_on_delete',
                               "Would you like to remove %s?" % self.source.get('target'),
                               default="yes")

    def install(self):
        self.__install_file(self.target)
        FormulaBase.install(self)

    def update(self):
        acted = False
        if self.target.has('on_update') and self.target.is_affirmative('on_update'):
            self.__install_file(self.target)
            acted = True
        FormulaBase.update(self)
        return acted

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
                source_content = lib.cleaned_request('get', source).text
        else:
            source_content = open(os.path.expanduser(source)).read()

        # replace {key} type markers in the template source
        if config.has('replacement_keys'):
            replacements = {}
            for key in config.get('replacement_keys').split(','):
                key = key.strip()
                if config.has(key):
                    replacements[key] = config.get(key)
            try:
                source_content = string.Formatter().vformat(
                    source_content, (), defaultdict(str, **replacements))
            except Exception as e:
                error_message = "Failed trying to format template! error: {err}".format(err=e.message)
                if config.is_affirmative('fail_on_error', False):
                    raise e
                else:
                    self.logger.error(error_message)

        target_file = os.path.expanduser(config.get('target'))
        parent_directory = os.path.dirname(target_file)
        if not os.path.exists(parent_directory):
            os.makedirs(parent_directory)

        # backup the template, if it is configured for it and if it has changed
        if os.path.isfile(target_file) and config.has('backup'):
            target_content = open(target_file).read()
            if target_content != source_content:
                backup_target_base = "{path}.{ext}".format(path=target_file, ext=config.get('backup'))
                backup_target = backup_target_base
                i = 1
                while os.path.isfile(backup_target):
                    backup_target = "{path}-{i}".format(path=backup_target_base, i=i)
                    i += 1
                self.logger.info("Backing up template target to %s..." % backup_target)
                os.rename(target_file, backup_target)
        with open(target_file, 'w+') as fh:
            fh.write(source_content)
