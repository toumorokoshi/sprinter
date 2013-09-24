from __future__ import unicode_literals
import logging
import os
import sys
import getpass
from six import reraise
from six.moves import configparser
from io import StringIO
from functools import wraps
from sprinter.core import PHASE
import sprinter.brew as brew
import sprinter.lib as lib
from sprinter.formulabase import FormulaBase
from sprinter.directory import Directory
from sprinter.exceptions import SprinterException
from sprinter.injections import Injections
from sprinter.manifest import Manifest
from sprinter.system import System
from sprinter.pippuppet import Pip, PipException
from sprinter.templates import shell_utils_template, source_template, warning_template


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
    sprinter_namespace = None  # the namespace to make installs with. this affects:
    phase = None  # the phase currently running
    # the prefix added to injections
    # the libraries that environment utilizes
    directory = None  # handles interactions with the environment directory
    injections = None  # handles injections
    global_injections = None  # handles injections for the global sprinter configuration
    system = None  # stores utility methods to determine system specifics
    # variables typically populated programatically
    warmed_up = False  # returns true if the environment is ready for environments
    shell_util_path = None  # the path to the shell utils file
    error_occured = False
    # A dictionary for class object instances. Exists Mainly for testability + injection
    formula_dict = {}
    # a dictionary of the feature objects.
    # The key is a tuple of feature name and formula, while the value is an instance.
    _feature_dict = {}
    # the order of the feature dict.
    _feature_dict_order = []
    # a dictionary of the errors associated with features.
    # The key is a tuple of feature name and formula, while the value is an instance.
    _error_dict = {}
    _errors = []  # list to keep all the errors
    # a pip puppet used to install eggs and add it to the classpath
    _pip = None
    sandboxes = []  # a list of package managers to sandbox (brew)
    # specifies where to get the global sprinter root
    global_config = None  # configuration file, which defaults to loading from SPRINTER_ROOT/.global/config.cfg
    write_files = True  # write files to the filesystem.

    def __init__(self, logger=None, logging_level=logging.INFO,
                 root=None, sprinter_namespace='sprinter',
                 global_config=None, write_files=True):
        self.system = System()
        if not logger:
            logger = self._build_logger(level=logging_level)
        self.logger = logger
        self.sprinter_namespace = sprinter_namespace
        self.root = root or os.path.expanduser(os.path.join("~", ".%s" % sprinter_namespace))
        self.global_path = os.path.join(self.root, ".global")
        self._pip = Pip(self.global_path)
        if logging_level == logging.DEBUG:
            self.logger.info("Starting in debug mode...")
        self.formula_dict = {}
        self.shell_util_path = os.path.join(self.global_path, "utils.sh")
        self.load_global_config(global_config)
        self.write_files = write_files
        
    @warmup
    def install(self):
        """ Install the environment """
        self.phase = PHASE.INSTALL
        if not self.directory.new:
            self.logger.info("Namespace %s already exists!" % self.namespace)
            self.source = Manifest(self.directory.manifest_path)
            return self.update()
        try:
            self.logger.info("Installing environment %s..." % self.namespace)
            self.directory.initialize()
            self.install_sandboxes()
            self.instantiate_features()
            self._specialize()
            for feature in self._feature_dict_order:
                self._run_action(feature, 'sync')
            self.inject_environment_config()
            self._finalize()
        except Exception:
            self.logger.debug("", exc_info=sys.exc_info())
            self.logger.info("An error occured during installation!")
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
            self.grab_inputs(reconfigure=reconfigure)
            self._specialize(reconfigure=reconfigure)
            for feature in self._feature_dict_order:
                self._run_action(feature, 'sync')
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
            for feature in self._feature_dict_order:
                self._run_action(feature, 'sync')
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
            for feature in self._feature_dict_order:
                self.logger.info("Deactivating %s..." % feature[0])
                self._run_action(feature, 'deactivate')
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
            for feature in self._feature_dict_order:
                self.logger.info("Activating %s..." % feature[0])
                self._run_action(feature, 'activate')
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
                context_dict['config:node'] = self.system.node
                self.target.add_additional_context(context_dict)
        for feature in self._feature_dict_order:
            self._run_action(feature, 'validate', run_if_error=True)

    @warmup
    def inject_environment_config(self):
        for shell in SHELL_CONFIG:
            if shell == 'gui':
                if self.system.isDebianBased():
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
                    if self.system.isOSX() and not self.injections.in_noninjected_file(env_path, rc_file):
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
            if self.system.isOSX():
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

    def run_feature(self, feature, action):
        for k in self._feature_dict_order:
            if feature in k:
                self._run_action(k, action, run_if_error=True)

    def write_debug_log(self, file_path):
        """ Write the debug log to a file """
        if self.write_files:
            with open(file_path, "w+") as fh:
                fh.write(self._debug_stream.getvalue())
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
        if os.path.exists(self.directory.manifest_path) and self.write_files:
            manifest = self.target or self.source
            manifest.write(open(self.directory.manifest_path, "w+"))

    def message_failure(self):
        """ return a failure message, if one exists """
        manifest = self.target or self.source
        if manifest and manifest.has_option('config', 'message_failure'):
            return manifest.get('config', 'message_failure')

    def message_success(self):
        """ return a success message, if one exists """
        manifest = self.target or self.source
        if manifest.has_option('config', 'message_success'):
            return manifest.get('config', 'message_success')

    def warmup(self):
        """ initialize variables necessary to perform a sprinter action """
        self.logger.debug("Warming up...")
        try:
            if not isinstance(self.source, Manifest) and self.source:
                self.source = Manifest(self.source)
            if not isinstance(self.target, Manifest) and self.target:
                self.target = Manifest(self.target)
        except lib.BadCredentialsException:
            e = sys.exc_info()[1]
            self.logger.error(str(e))
            raise SprinterException("Fatal error! Bad credentials to grab manifest!")
        if self.target:
            self.namespace = self.target.namespace
        if not self.namespace and self.source:
            self.namespace = self.source.namespace
        if not self.directory:
            self.directory = Directory(self.namespace,
                                       sprinter_root=self.root,
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

    def instantiate_features(self):
        """ Create and instantiate the feature dictionary """
        self._feature_dict = {}
        self._feature_dict_order = []

        if self.target:
            for feature in self.target.formula_sections():
                feature_key = self._instantiate_feature(
                    feature, self.target.get_feature_config(feature), 'target')
                if feature_key:
                    self._feature_dict_order.append(feature_key)
        if self.source:
            for feature in self.source.formula_sections():
                feature_key = self._instantiate_feature(
                    feature, self.source.get_feature_config(feature), 'source')
                if feature_key:
                    self._feature_dict_order.insert(0, feature_key)

    def _instantiate_feature(self, feature, feature_config, kind):
        if feature_config.has('formula'):
            key = (feature, feature_config.get('formula'))
            if key not in self._feature_dict:
                try:
                    formula_class = self._get_formula_class(feature_config.get('formula'))
                    self._feature_dict[key] = formula_class(self, feature, **{kind: feature_config})
                    self._error_dict[key] = []
                    if self._feature_dict[key].should_run():
                        return key
                    else:
                        del(self._feature_dict[key])
                except SprinterException:
                    self.log_error("ERROR: Invalid formula %s for %s feature %s!"
                                   % (feature_config.get('formula'), kind, feature))
            else:
                setattr(self._feature_dict[key], kind, feature_config)
        else:
            self.log_error('feature %s has no formula!' % feature)
        return None

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
            manifest = self.target or self.source
            if self.system.isOSX() and manifest.is_affirmative('config', 'use_global_packagemanagers'):
                self.directory.add_to_env('sprinter_prepend_path "%s" PATH' % '/usr/local/bin/')
            self.directory.add_to_env('sprinter_prepend_path "%s" PATH' % self.directory.bin_path())
            self.directory.add_to_env('sprinter_prepend_path "%s" LIBRARY_PATH' % self.directory.lib_path())
            self.directory.add_to_env('sprinter_prepend_path "%s" C_INCLUDE_PATH' % self.directory.include_path())
        if self.write_files:
            self.injections.commit()
            self.global_injections.commit()
            if not os.path.exists(os.path.join(self.root, ".global")):
                self.logger.debug("Global directoy doesn't exist! creating...")
                os.makedirs(os.path.join(self.root, ".global"))
            self.logger.debug("Writing global config...")
            self.global_config.write(open(os.path.join(self.root, ".global", "config.cfg"), 'w+'))
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

    def _get_formula_class(self, formula):
        """
        get a formula class object if it exists, else
        create one, add it to the dict, and pass return it.
        """
        formula_class, formula_url = formula, None
        if ':' in formula:
            formula_class, formula_url = formula.split(":", 1)
        if formula_class not in self.formula_dict:
            try:
                self.formula_dict[formula_class] = lib.get_subclass_from_module(formula_class, FormulaBase)
            except (SprinterException, ImportError):
                self.logger.info("Downloading %s..." % formula_class)
                try:
                    self._pip.install_egg(formula_url or formula_class)
                    try:
                        self.formula_dict[formula_class] = lib.get_subclass_from_module(formula_class, FormulaBase)
                    except ImportError:
                        raise SprinterException("Error: Unable to retrieve formula %s!" % formula_class)
                except PipException:
                    self.logger.error("ERROR: Unable to download %s!" % formula_class)
        return self.formula_dict[formula_class]

    def log_error(self, error_message):
        self.error_occured = True
        self._errors += [error_message]
        self.logger.error(error_message)

    def log_feature_error(self, feature, error_message):
        self.error_occured = True
        self._error_dict[feature] += [error_message]
        self.logger.error(error_message)
            
    def _run_action(self, feature, action, run_if_error=False):
        """ Run an action, and log it's output in case of errors """
        if len(self._error_dict[feature]) > 0 and not run_if_error:
            return
        instance = self._feature_dict[feature]
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
                    context_dict['config:node'] = self.system.node
                manifest.add_additional_context(context_dict)
        self.grab_inputs()
        for feature in self._feature_dict_order:
            self._run_action(feature, 'validate', run_if_error=True)
            if not reconfigure:
                self._run_action(feature, 'resolve')
            self._run_action(feature, 'prompt')

    def grab_inputs(self, reconfigure=False):
        """ Resolve the source and target config section """
        if self.source:
            if self.target:
                for k, v in self.source.items('config'):
                    if not self.target.has_option('config', k):
                        self.target.set('config', k, v)
        if self.target:
            self.target.grab_inputs(force_prompt=reconfigure)

    def load_global_config(self, global_config_string):
        if self.global_config:
            return self.global_config
        self.global_config = configparser.RawConfigParser()
        if global_config_string:
            self.global_config.readfp(StringIO(global_config_string))
        else:
            global_config_path = os.path.join(self.root, ".global", "config.cfg")
            if os.path.exists(global_config_path):
                self.global_config.read(global_config_path)
                self.logger.info("Checking and setting global parameters...")
            else:
                self.initial_run()  # it's probably the first run, so stick initial run logic in here
                self.logger.info("Unable to find a global sprinter configuration!")
                self.logger.info("Creating one now. Please answer some questions" +
                                 " about what you would like sprinter to do.")
                self.logger.info("")
            if not self.global_config.has_section('shell'):
                # shell configuration
                self.global_config.add_section('shell')
                self.logger.info("What shells or environments would you like sprinter to work with?\n" +
                                 "(Sprinter will not try to inject into environments not specified here.)\n" +
                                 "If you specify 'gui', sprinter will attempt to inject it's state into graphical programs as well.\n" +
                                 "i.e. environment variables sprinter set will affect programs as well, not just shells")
                environments = list(enumerate(sorted(SHELL_CONFIG), start=1))
                self.logger.info("[0]: All, " + ", ".join(["[%d]: %s" % (index, val) for index, val in environments]))
                desired_environments = lib.prompt("type the environment, comma-separated", default="0")
                for index, val in environments:
                    if str(index) in desired_environments or "0" in desired_environments:
                        self.global_config.set('shell', val, 'true')
                    else:
                        self.global_config.set('shell', val, 'false')
            if not self.global_config.has_section('global'):
                self.global_config.add_section('global')
            if not self.global_config.has_option('global', 'env_source_rc'):
                self.global_config.set('global', 'env_source_rc', False)
                if self.system.isOSX():
                    self.logger.info("On OSX, login shells are default, which only source sprinter's 'env' configuration.")
                    self.logger.info("I.E. environment variables would be sourced, but not shell functions "
                                     + "or terminal status lines.")
                    self.logger.info("The typical solution to get around this is to source your rc file (.bashrc, .zshrc) "
                                     + "from your login shell.")
                    env_source_rc = lib.prompt("would you like sprinter to source the rc file too?", default="yes",
                                               boolean=True)
                    self.global_config.set('global', 'env_source_rc', env_source_rc)

    def initial_run(self):
        """ A method that only runs during the initial run of sprinter """
        if not self.system.is_officially_supported():
            self.logger.warn(warning_template
                             + "===========================================================\n"
                             + "Sprinter is not officially supported on {0}! Please use at your own risk.\n\n".format(self.system.operating_system())
                             + "You can find the supported platforms here:\n"
                             + "(http://sprinter.readthedocs.org/en/latest/index.html#compatible-systems)\n\n"
                             + "Conversely, please help us support your system by reporting on issues\n"
                             + "(http://sprinter.readthedocs.org/en/latest/faq.html#i-need-help-who-do-i-talk-to)\n"
                             + "===========================================================")
