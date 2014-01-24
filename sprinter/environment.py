from __future__ import unicode_literals
import logging
import os
import sys
import getpass
from six import reraise
from io import StringIO
from functools import wraps
from collections import defaultdict

import sprinter.lib as lib
from sprinter.core import PHASE, load_global_config, Directory, Injections, Manifest, load_manifest, FeatureDict
from sprinter.core.templates import shell_utils_template, source_template
from sprinter.lib import SprinterException, system
from sprinter.external import brew


def warmup(f):
    """ Decorator to run warmup before running a command """

    @wraps(f)
    def wrapped(self, *args, **kwargs):
        if not self.warmed_up:
            self.warmup()
        return f(self, *args, **kwargs)
    return wrapped


def install_required(f):
    """ Return an exception if the namespace is not already installed """

    @wraps(f)
    def wrapped(self, *args, **kwargs):
        if self.directory.new:
            raise SprinterException("Namespace %s is not yet installed!" % self.namespace)
        return f(self, *args, **kwargs)
    return wrapped

# http://www.gnu.org/software/bash/manual/bashref.html#Bash-Startup-Files
# http://zsh.sourceforge.net/Guide/zshguide02.html
SHELL_CONFIG = {
    'bash': {
        'rc': ['.bashrc'],
        'env': ['.bash_profile', '.bash_login', '.profile']
    },
    'zsh': {
        'rc': ['.zshrc'],
        'env': ['.zprofile', '.zlogin']
    },
    'gui': {
        'debian': ['.profile'],
        'osx': lib.insert_environment_osx
    }
}

# for now, they are all still dealt with en masse
RC_FILES = []
ENV_FILES = []

for shell, shell_config in SHELL_CONFIG.items():
    if shell != 'gui':
        RC_FILES += shell_config['rc']
        ENV_FILES += shell_config['env']

CONFIG_FILES = RC_FILES + ENV_FILES


class Environment(object):

    source = None  # the path to the source handle, the handle itself, or a manifest instance
    target = None  # the path to the target handle, the handle itself, or a manifest instance
    namespace = None  # the namespace of the environment
    custom_directory_root = None  # the root to install directories too
    do_inject_environment_config = True  # inject configuration into shells
    sprinter_namespace = None  # the namespace to make installs with. this affects:
    phase = None  # the phase currently running
    # the prefix added to injections
    # the libraries that environment utilizes
    directory = None  # handles interactions with the environment directory
    injections = None  # handles injections
    global_injections = None  # handles injections for the global sprinter configuration
    # variables typically populated programatically
    warmed_up = False  # returns true if the environment is ready for environments
    shell_util_path = None  # the path to the shell utils file
    error_occured = False
    _errors = []  # list to keep all the errors
    sandboxes = []  # a list of package managers to sandbox (brew)
    # specifies where to get the global sprinter root
    global_config = None  # configuration file, which defaults to loading from SPRINTER_ROOT/.global/config.cfg
    ignore_errors = False  # ignore errors in features

    def __init__(self,
                 logger=None,
                 logging_level=logging.INFO,
                 root=None,
                 sprinter_namespace=None,
                 global_config=None,
                 ignore_errors=False):

        # base logging object to log instances
        self.logger = logger or self._build_logger(level=logging_level)
        if logging_level == logging.DEBUG:
            self.logger.info("Starting in debug mode...")

        # the sprinter namespace
        self.sprinter_namespace = sprinter_namespace or 'sprinter'

        # the root directory which sprinter installs sandboxable files too
        self.root = root or os.path.expanduser(os.path.join("~", ".%s" % self.sprinter_namespace))

        self.ignore_errors = ignore_errors

        # path to the directory to install global files
        self.global_path = os.path.join(self.root, ".global")
        self.global_config_path = os.path.join(self.global_path, "config.cfg")
        self.global_config = global_config or load_global_config(self.global_config_path)
        
        self.shell_util_path = os.path.join(self.global_path, "utils.sh")
        self.main_manifest = None

        # a dictionary of the errors associated with features.
        # The key is a tuple of feature name and formula, while the value is an instance.
        self._error_dict = defaultdict(list)
        
    @warmup
    def install(self):
        """ Install the environment """
        self.phase = PHASE.INSTALL
        if not self.directory.new:
            self.logger.info("Namespace %s directory already exists!" % self.namespace)
            self.source = load_manifest(self.directory.manifest_path)
            return self.update()
        try:
            self.logger.info("Installing environment %s..." % self.namespace)
            self.directory.initialize()
            self.install_sandboxes()
            self.instantiate_features()
            self.grab_inputs()
            self._specialize()
            for feature in self.features.run_order:
                self.run_action(feature, 'sync')
            self.inject_environment_config()
            self._finalize()
        except Exception:
            self.logger.debug("", exc_info=sys.exc_info())
            self.logger.info("An error occured during installation!")
            if not self.ignore_errors:
                self.clear_all()
                self.logger.info("Removing installation %s..." % self.namespace)
                self.directory.remove()
                et, ei, tb = sys.exc_info()
                reraise(et, ei, tb)
        
    @warmup
    @install_required
    def update(self, reconfigure=False):
        """ update the environment """
        try:
            self.phase = PHASE.UPDATE
            self.logger.info("Updating environment %s..." % self.namespace)
            self.install_sandboxes()
            self.instantiate_features()
            # We don't grab inputs, only on install
            # updates inputs are grabbed on demand
            # self.grab_inputs(reconfigure=reconfigure)
            if reconfigure:
                self.grab_inputs(reconfigure=True)
            else:
                self._copy_source_to_target()
            self._specialize(reconfigure=reconfigure)
            for feature in self.features.run_order:
                self.run_action(feature, 'sync')
            self.inject_environment_config()
            self._finalize()
        except Exception:
            self.logger.debug("", exc_info=sys.exc_info())
            et, ei, tb = sys.exc_info()
            reraise(et, ei, tb)

    @warmup
    @install_required
    def remove(self):
        """ remove the environment """
        try:
            self.phase = PHASE.REMOVE
            self.logger.info("Removing environment %s..." % self.namespace)
            self.instantiate_features()
            self._specialize()
            for feature in self.features.run_order:
                self.run_action(feature, 'sync')
            self.clear_all()
            self.directory.remove()
            self.injections.commit()
        except Exception:
            self.logger.debug("", exc_info=sys.exc_info())
            et, ei, tb = sys.exc_info()
            reraise(et, ei, tb)

    @warmup
    @install_required
    def deactivate(self):
        """ deactivate the environment """
        try:
            self.phase = PHASE.DEACTIVATE
            self.logger.info("Deactivating environment %s..." % self.namespace)
            self.directory.rewrite_config = False
            self.instantiate_features()
            self._specialize()
            for feature in self.features.run_order:
                self.logger.info("Deactivating %s..." % feature[0])
                self.run_action(feature, 'deactivate')
            self.clear_all()
            self._finalize()
        except Exception:
            self.logger.debug("", exc_info=sys.exc_info())
            et, ei, tb = sys.exc_info()
            reraise(et, ei, tb)

    @warmup
    @install_required
    def activate(self):
        """ activate the environment """
        try:
            self.phase = PHASE.ACTIVATE
            self.logger.info("Activating environment %s..." % self.namespace)
            self.directory.rewrite_config = False
            self.instantiate_features()
            self._specialize()
            for feature in self.features.run_order:
                self.logger.info("Activating %s..." % feature[0])
                self.run_action(feature, 'activate')
            self.inject_environment_config()
            self._finalize()
        except Exception:
            self.logger.debug("", exc_info=sys.exc_info())
            et, ei, tb = sys.exc_info()
            reraise(et, ei, tb)

    @warmup
    def validate(self):
        """ Validate the target environment """
        self.phase = PHASE.VALIDATE
        self.logger.info("Validating %s..." % self.namespace)
        self.instantiate_features()
        context_dict = {}
        if self.target:
            for s in self.target.formula_sections():
                context_dict["%s:root_dir" % s] = self.directory.install_directory(s)
                context_dict['config:root_dir'] = self.directory.root_dir
                context_dict['config:node'] = system.NODE
                self.target.add_additional_context(context_dict)
        for feature in self.features.run_order:
            self.run_action(feature, 'validate', run_if_error=True)

    @warmup
    def inject_environment_config(self):
        if not self.do_inject_environment_config:
            return

        for shell in SHELL_CONFIG:
            if shell == 'gui':
                if system.is_debian():
                    self._inject_config_source(".env", SHELL_CONFIG['gui']['debian'])
            else:
                if (self.global_config.has_option('shell', shell)
                   and lib.is_affirmative(self.global_config.get('shell', shell))):

                    rc_file, rc_path = self._inject_config_source(".rc", SHELL_CONFIG[shell]['rc'])
                    env_file, env_path = self._inject_config_source(".env", SHELL_CONFIG[shell]['env'])
                    # If an rc file is sourced by an env file, we should alert the user.
                    if (self.phase is PHASE.INSTALL
                       and self.injections.in_noninjected_file(env_path, rc_file)
                       and self.global_injections.in_noninjected_file(env_path, rc_file)):
                        self.logger.info("You appear to be sourcing %s from inside %s." % (rc_file, env_file))
                        self.logger.info("Please ensure it is wrapped in a #SPRINTER_OVERRIDES block " +
                                         "to avoid repetitious operations!")
                    full_rc_path = os.path.expanduser(os.path.join("~", rc_file))
                    full_env_path = os.path.expanduser(os.path.join("~", env_file))
                    if lib.is_affirmative(self.global_config.get('global', 'env_source_rc')):
                        self.global_injections.inject(
                            full_env_path,
                            source_template % (full_rc_path, full_rc_path))
                    else:
                        self.global_injections.inject(full_env_path, '')
                    if system.is_osx() and not self.injections.in_noninjected_file(env_path, rc_file):
                        if self.phase is PHASE.INSTALL:
                            self.logger.info("On OSX, login shell are the default, which only source config files")

    @warmup
    def clear_all(self):
        """ clear all files that were to be injected """
        self.injections.clear_all()
        for config_file in CONFIG_FILES:
            self.injections.clear(os.path.join("~", config_file))

    def install_sandboxes(self):
        if self.target:
            if system.is_osx():
                if not self.target.is_affirmative('config', 'use_global_packagemanagers'):
                    self._install_sandbox('brew', brew.install_brew)
                elif lib.which('brew') is None:
                    install_brew = lib.prompt(
                        "Looks like you don't have brew, " +
                        "which is sprinter's package manager of choice for OSX.\n"
                        "Would you like sprinter to install brew for you?",
                        default="yes", boolean=True)
                    if install_brew:
                        lib.call("sudo mkdir -p /usr/local/", stdout=None,
                                 output_log_level=logging.DEBUG)
                        lib.call("sudo chown -R %s /usr/local/" % getpass.getuser(),
                                 output_log_level=logging.DEBUG, stdout=None)
                        brew.install_brew('/usr/local')

    def instantiate_features(self):
        if hasattr(self, 'features') and self.features:
            return
        self.features = FeatureDict(self,
                                    self.source, self.target,
                                    self.global_path)

    def run_feature(self, feature, action):
        for k in self.features.run_order:
            if feature in k:
                self.run_action(k, action, run_if_error=True)

    def write_debug_log(self, file_path):
        """ Write the debug log to a file """
        with open(file_path, "w+") as fh:
            fh.write(system.get_system_info())
            # writing to debug stream
            self._debug_stream.seek(0)
            fh.write(self._debug_stream.read())
            fh.write("The following errors occured:\n")
            for error in self._errors:
                fh.write(error + "\n")
            for k, v in self._error_dict.items():
                if len(v) > 0:
                    fh.write("Error(s) in %s with formula %s:\n" % k)
                    for error in v:
                        fh.write(error + "\n")

    def write_manifest(self):
        """ Write the manifest to the file """
        if os.path.exists(self.directory.manifest_path):
            self.main_manifest.write(open(self.directory.manifest_path, "w+"))

    def message_failure(self):
        """ return a failure message, if one exists """
        if not isinstance(self.main_manifest, Manifest):
            return None
        return self.main_manifest.get('config', 'message_failure', default=None)

    def message_success(self):
        """ return a success message, if one exists """
        return self.main_manifest.get('config', 'message_success', default=None)

    def warmup(self):
        """ initialize variables necessary to perform a sprinter action """
        self.logger.debug("Warming up...")

        try:
            if not isinstance(self.source, Manifest) and self.source:
                self.source = load_manifest(self.source)
            if not isinstance(self.target, Manifest) and self.target:
                self.target = load_manifest(self.target)
            self.main_manifest = self.target or self.source
        except lib.BadCredentialsException:
            e = sys.exc_info()[1]
            self.logger.error(str(e))
            raise SprinterException("Fatal error! Bad credentials to grab manifest!")

        if not getattr(self, 'namespace', None):
            if self.target:
                self.namespace = self.target.namespace
            elif not self.namespace and self.source:
                self.namespace = self.source.namespace
            else:
                raise SprinterException("No environment name has been specified!")

        self.directory_root = self.custom_directory_root

        if not self.directory:
            if not self.directory_root:
                self.directory_root = os.path.join(self.root, self.namespace)

            self.directory = Directory(self.directory_root,
                                       shell_util_path=self.shell_util_path)

        if not self.injections:
            self.injections = Injections(wrapper="%s_%s" % (self.sprinter_namespace.upper(),
                                                            self.namespace),
                                         override="SPRINTER_OVERRIDES")
        if not self.global_injections:
            self.global_injections = Injections(wrapper="%s" % self.sprinter_namespace.upper() + "GLOBALS",
                                                override="SPRINTER_OVERRIDES")
        # append the bin, in the case sandboxes are necessary to
        # execute commands further down the sprinter lifecycle
        os.environ['PATH'] = self.directory.bin_path() + ":" + os.environ['PATH']
        self.warmed_up = True

    def _inject_config_source(self, source_filename, files_to_inject):
        """
        Inject existing environmental config with namespace sourcing.
        Returns a tuple of the first file name and path found.
        """
        # src_path = os.path.join(self.directory.root_dir, source_filename)
        # src_exec = "[ -r %s ] && . %s" % (src_path, src_path)
        src_exec = "[ -r %s/%s ] && . %s/%s" % (self.directory.root_dir, source_filename,
                                                self.directory.root_dir, source_filename)
        # The ridiculous construction above is necessary to avoid failing tests(!)

        for config_file in files_to_inject:
            config_path = os.path.expanduser(os.path.join("~", config_file))
            if os.path.exists(config_path):
                self.injections.inject(config_path, src_exec)
                break
        else:
            config_file = files_to_inject[0]
            config_path = os.path.expanduser(os.path.join("~", config_file))
            self.logger.info("No config files found to source %s, creating ~/%s!" % (source_filename, config_file))
            self.injections.inject(config_path, src_exec)

        return (config_file, config_path)

    def _finalize(self):
        """ command to run at the end of sprinter's run """
        self.logger.info("Finalizing...")
        self.write_manifest()

        if self.directory.rewrite_config:
            # always ensure .rc is written (sourcing .env)
            self.directory.add_to_rc('')
            # prepend brew for global installs
            if system.is_osx() and self.main_manifest.is_affirmative('config', 'use_global_packagemanagers'):
                self.directory.add_to_env('__sprinter_prepend_path "%s" PATH' % '/usr/local/bin')
            self.directory.add_to_env('__sprinter_prepend_path "%s" PATH' % self.directory.bin_path())
            self.directory.add_to_env('__sprinter_prepend_path "%s" LIBRARY_PATH' % self.directory.lib_path())
            self.directory.add_to_env('__sprinter_prepend_path "%s" C_INCLUDE_PATH' % self.directory.include_path())

        self.injections.commit()
        self.global_injections.commit()

        if not os.path.exists(os.path.join(self.root, ".global")):
            self.logger.debug("Global directory doesn't exist! creating...")
            os.makedirs(os.path.join(self.root, ".global"))

        self.logger.debug("Writing global config...")
        self.global_config.write(open(self.global_config_path, 'w+'))

        self.logger.debug("Writing shell util file...")
        with open(self.shell_util_path, 'w+') as fh:
            fh.write(shell_utils_template)

        if self.error_occured:
            raise SprinterException("Error occured!")

        if self.message_success():
            self.logger.info(self.message_success())

        self.logger.info("NOTE: Please remember to open new shells/terminals to use the modified environment")

    def _install_sandbox(self, name, call, kwargs={}):
        if (self.target.is_affirmative('config', name) and
           (not self.source or not self.source.is_affirmative('config', name))):
            self.logger.info("Installing %s..." % name)
            call(self.directory.root_dir, **kwargs)

    def _build_logger(self, level=logging.INFO):
        """ return a logger. if logger is none, generate a logger from stdout """
        self._debug_stream = StringIO()
        logger = logging.getLogger('sprinter')
        # stdout log
        out_hdlr = logging.StreamHandler(sys.stdout)
        out_hdlr.setLevel(level)
        logger.addHandler(out_hdlr)
        # debug log
        debug_hdlr = logging.StreamHandler(self._debug_stream)
        debug_hdlr.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
        debug_hdlr.setLevel(logging.DEBUG)
        logger.addHandler(debug_hdlr)
        logger.setLevel(logging.DEBUG)
        return logger

    def log_error(self, error_message):
        self.error_occured = True
        self._errors += [error_message]
        self.logger.error(error_message)

    def get_error_value(self, feature):
        """ get the error value for a feature """
        if feature not in self._error_dict:
            self._error_dict1

    def log_feature_error(self, feature, error_message):
        self.error_occured = True
        self._error_dict[feature] += [error_message]
        self.logger.error(error_message)
            
    def run_action(self, feature, action, run_if_error=False):
        """ Run an action, and log it's output in case of errors """
        if len(self._error_dict[feature]) > 0 and not run_if_error:
            return
        instance = self.features[feature]
        try:
            result = getattr(instance, action)()
            if result:
                if type(result) != list:
                    self.log_feature_error(feature,
                                           "Error occurred! %s" % str(result))
                else:
                    self._error_dict[feature] += result
            if len(self._error_dict[feature]) > 0:
                self.error_occured = True
        # catch a generic exception within a feature
        except Exception:
            e = sys.exc_info()[1]
            self.logger.info("An exception occurred with action %s in feature %s!" %
                             (action, feature))
            self.logger.debug("Exception", exc_info=sys.exc_info())
            self.log_feature_error(feature, str(e))

    def _specialize(self, reconfigure=False):
        """ Add variables and specialize contexts """
        # add in the 'root_dir' directories to the context dictionaries
        for manifest in [self.source, self.target]:
            context_dict = {}
            if manifest:
                for s in manifest.formula_sections():
                    context_dict["%s:root_dir" % s] = self.directory.install_directory(s)
                    context_dict['config:root_dir'] = self.directory.root_dir
                    context_dict['config:node'] = system.NODE
                manifest.add_additional_context(context_dict)
        for feature in self.features.run_order:
            self.run_action(feature, 'validate', run_if_error=True)
            if not reconfigure:
                self.run_action(feature, 'resolve')
            self.run_action(feature, 'prompt')

    def _copy_source_to_target(self):
        """ copy source user configuration to target """
        if self.source and self.target:
            for k, v in self.source.items('config'):
                # always have source override target.
                self.target.set_input(k, v)

    def grab_inputs(self, reconfigure=False):
        """ Resolve the source and target config section """
        self._copy_source_to_target()
        if self.target:
            self.target.grab_inputs(force=reconfigure)
