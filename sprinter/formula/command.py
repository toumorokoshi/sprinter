"""
Runs a command
[ssh]
formula = sprinter.formula.command
hideoutput=true
fail_on_error=true
shell = False
install=echo 'setting up...'
update=echo 'updating...'
remove=echo 'destroying...'
activate=echo 'activating...'
deactivate=echo 'deactivating...'
"""
from __future__ import unicode_literals
from sprinter.formula.base import FormulaBase
import sprinter.lib as lib

class CommandFormulaException(Exception):
    pass

class CommandFormula(FormulaBase):

    valid_options = FormulaBase.valid_options + ['install', 'update', 'remove', 'activate', 'deactivate', 'fail_on_error', 'shell']

    def install(self):
        self.__run_command('install', 'target')
        FormulaBase.install(self)

    def update(self):
        self.__run_command('update', 'target')
        FormulaBase.update(self)

    def remove(self):
        self.__run_command('remove', 'source')
        FormulaBase.remove(self)

    def activate(self):
        self.__run_command('activate', 'source')
        FormulaBase.activate(self)

    def deactivate(self):
        self.__run_command('deactivate', 'source')
        FormulaBase.deactivate(self)

    def __run_command(self, command_type, manifest_type):
        config = getattr(self, manifest_type)
        if config.has(command_type):
            command = config.get(command_type)
            self.logger.debug("Running %s..." % command)
            shell = config.has('shell') and config.is_affirmative('shell')
            return_code, output = lib.call(command, shell=shell)
            if config.is_affirmative('fail_on_error', True) and return_code != 0:
                raise CommandFormulaException("Command returned a return code of {0}!".format(return_code))
