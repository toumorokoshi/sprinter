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
from sprinter.exceptions import FormulaException
import sprinter.lib as lib
import subprocess


class CommandFormulaException(FormulaException):
    pass


class CommandFormula(FormulaBase):

    valid_options = FormulaBase.valid_options + ['install',
                                                 'update',
                                                 'remove',
                                                 'activate',
                                                 'deactivate',
                                                 'fail_on_error',
                                                 'shell',
                                                 'redirect_stdout_to_log']

    def install(self):
        self._run_command('install')
        FormulaBase.install(self)

    def update(self):
        value = self._run_command('update')
        return value or FormulaBase.update(self)

    def remove(self):
        self._run_command('remove')
        FormulaBase.remove(self)

    def activate(self):
        self._run_command('activate')
        FormulaBase.activate(self)

    def deactivate(self):
        self._run_command('deactivate')
        FormulaBase.deactivate(self)

    def _run_command(self, command_type):
        if self.config.has(command_type):
            command = self.config.get(command_type)
            self.logger.debug("Running %s..." % command)
            shell = self.config.is_affirmative("shell", default="no")
            stdout = subprocess.PIPE if self.config.is_affirmative('redirect_stdout_to_log', 'true') else None
            return_code, output = lib.call(command, shell=shell, stdout=stdout)
            if self.config.is_affirmative('fail_on_error', default="yes") and return_code != 0:
                raise CommandFormulaException("Command returned a return code of {0}!".format(return_code))
            return True
