"""
Formula base is an abstract base class outlining the method required
and some documentation on what they should provide.
"""
from __future__ import unicode_literals
import logging
import os

from sprinter.core import PHASE
from sprinter.exceptions import FormulaException
from sprinter.lib import system
import sprinter.lib as lib


class FormulaBase(object):
    """
    This is the base class for all Sprinter formulas. All classes
    should extend from FormulaBase: it is used as part of the
    package resolution scheme, and will not be recognized otherwise.

    All sprinter formulas should honor a default set of fields. Those
    fields are:

    * formula (required): read by sprinter to resolve the Formula to load.
    * rc (str): a string to inject into the rc file of the shell environment
    * env (str): a string to inject in to the profile file of the shell environment
    * gui (str): a string to inject into the gui file of the os environment
    * command (str): an optional command to run, after executing the formula
    * systems (str):
        a whitelist of the valid systems that this formula can be installed
        in (no value means all systems)
    * depends (List[str], comma separated):
        a list of other formulas that must execute, before this formula.

    Those options are:
    """

    valid_options = ["rc", "env", "gui", "command", "systems", "depends", "inputs"]
    required_options = ["formula"]
    deprecated_options = []

    # these values will not carry over from source to target
    dont_carry_over_options = valid_options + required_options

    def __init__(self, environment, feature_name, source=None, target=None):
        """
        In most cases, it is not a good idea to override the formulabase
        init method. Sprinter calls it in a very specific fashion, and
        to set it up otherwise risks incompatibility

        :param feature_name: the name of the feature being installed
        """
        self.logger = logging.getLogger("sprinter.formula." + type(self).__name__)
        self.feature_name = feature_name
        self.source = source
        self.target = target
        self.environment = environment
        self.directory = environment.directory
        self.injections = environment.injections

    def prompt(self):
        """
        This call should contain as much of the user input as possible. Examples include:

        * prompting for options regarding configuration
        * overriding existing files/configuration

        prompt's are brought up at the beginning of sprinter's
        instantiation, before any action's are taken.
        """

    def install(self):
        """
        Install is called when a feature does not previously exist.

        In the case of a feature changing formulas, the old feature/formula is
        removed, then the new feature/formula is installed.

        Installs are only guaranteed to have the 'target' config set.

        errors should either be reported via self._log_error(), or raise an exception
        """
        return

    def update(self):
        """
        Update is called when a feature previously exists, with the same formula

        Updates are guaranteed to have both the 'source' and 'target' configs set

        errors should either be reported via self._log_error(), or raise an exception
        """
        return

    def remove(self):
        """
        Remove is called when a feature no longer exists.

        remove will delete the feature directory before it is
        done. Most of the time, no other action should be necessary.

        remove is guaranteed to have only the 'source' config.

        errors should either be reported via self._log_error(), or raise an exception
        """
        return True

    def deactivate(self):
        """
        Deactivate is called when a user deactivates the environment.

        deactivate will deactivate an environment. Deactivate disables
        the .rc file for a sprinter install, so any extra functionality
        should be removed here:

        * configuration in a global location, such as an ssh configuration

        errors should either be reported via self._log_error(), or raise an exception
        """

    def activate(self):
        """
        Activate is called when a user activates the environment.

        activate should inject configuration into the environment. Activate enables the .rc file for a sprinter install,
        so any extra functionality should be added here:

        * configuration in a global location, such as an ssh configuration

        errors should either be reported via self._log_error(), or raise an exception
        """

    def validate(self):
        """
        validates the feature configuration, and returns a list of errors (empty list if no error)

        validate should:

        * required variables
        * warn on unused variables

        errors should either be reported via self._log_error(), or raise an exception
        """
        if self.target:
            for k in self.target.keys():
                if k in self.deprecated_options:
                    self.logger.warn(
                        self.deprecated_options[k].format(
                            option=k, feature=self.feature_name
                        )
                    )
                elif (
                    k not in self.valid_options
                    and k not in self.required_options
                    and "*" not in self.valid_options
                ):
                    self.logger.warn("Unused option %s in %s!" % (k, self.feature_name))
            for k in self.required_options:
                if not self.target.has(k):
                    self._log_error(
                        "Required option %s not present in feature %s!"
                        % (k, self.feature_name)
                    )

    # these methods are overwritten less often, and are not recommended to do so.
    def should_run(self):
        """Returns true if the feature should run"""
        should_run = True
        config = self.target or self.source
        if config.has("systems"):
            should_run = False
            valid_systems = [s.lower() for s in config.get("systems").split(",")]
            for system_type, param in [("is_osx", "osx"), ("is_debian", "debian")]:
                if param in valid_systems and getattr(system, system_type)():
                    should_run = True
        return should_run

    def resolve(self):
        """Resolve differences between the target and the source configuration"""
        if self.source and self.target:
            for key in self.source.keys():
                if key not in self.dont_carry_over_options and not self.target.has(key):
                    self.target.set(key, self.source.get(key))

    def _log_error(self, message):
        """Log an error for the feature"""
        key = (self.feature_name, self.target.get("formula"))
        self.environment.log_feature_error(key, "ERROR: " + message)

    def _prompt_value(self, key, prompt_string, default=None, only_if_empty=True):
        """prompts the user for a value, and saves it to either the target or
        source manifest (whichever is appropriate for the phase)

        this method takes will default to the original value passed by
        the user in the case one exists. e.g. if a user already
        answered 'yes' to a question, it will use 'yes' as the default
        vs the one passed into this method.
        """
        main_manifest = self.target or self.source

        if only_if_empty and main_manifest.has(key):
            return main_manifest.get(key)

        prompt_default = default
        if self.source and self.source.has(key):
            prompt_default = self.source.get(key)

        main_manifest.set(key, lib.prompt(prompt_string, default=prompt_default))

    # utility methods
    def _install_directory(self):
        """
        return the path to the directory available for the feature to put
        files in
        """
        return self.directory.install_directory(self.feature_name)
