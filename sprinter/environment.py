import logging
import os
import sys
from StringIO import StringIO

from sprinter import virtualenv
from sprinter import brew
from sprinter import lib
from sprinter.directory import Directory
from sprinter.exceptions import SprinterException
from sprinter.injections import Injections
from sprinter.lib import get_formula_class
from sprinter.manifest import Config, Manifest, ManifestException
from sprinter.system import System


def warmup(f):
    """ Decorator to run warmup before running a command """

    def wrapped(self, *args, **kwargs):
        if not self.warmed_up:
            self._warmup()
        return f(self, *args, **kwargs)
    return wrapped


def install_required(f):
    """ Return an exception if the namespace is not already installed """

    def wrapped(self, *args, **kwargs):
        if self.directory.new:
            raise SprinterException("Namespace %s is not yet installed!" % self.namespace)
        return f(self, *args, **kwargs)
    return wrapped


def populate_formula_instance(config):
    """ Populate the formula_instance variable if it is none, from the formula config specified """

    def wrapper(f):

        def wrapped(self, feature_name, formula_instance=None):
            if not formula_instance:
                try:
                    formula_instance = self._get_formula_instance(
                        getattr(self, config).get_feature_class(feature_name))
                except ManifestException:
                    self.logger.warn("Unable to retrieve formula for feature %s!" % feature_name)
                except ImportError:
                    self.logger.warn("Unable to retrieve formula for feature %s!" % feature_name)
            if not formula_instance:
                return None
            return f(self, feature_name, formula_instance=formula_instance)
        return wrapped
    return wrapper


class Environment(object):

    source = None  # the path to the source handle, the handle itself, or a manifest instance
    target = None  # the path to the target handle, the handle itself, or a manifest instance
    namespace = None  # the namespace of the environment
    sandboxes = []  # a list of package managers to sandbox (brew, virtualenv)
    # the libraries that environment utilizes
    config = None  # handles the configuration, and manifests
    directory = None  # handles interactions with the environment directory
    injections = None  # handles injections
    system = None  # stores utility methods to determine system specifics
    lib = lib  # utility library
    # variables typically populated programatically
    warmed_up = False  # returns true if the environment is ready for environments
    _formula_dict = {}  # a dictionary of existing formula instances to pull from
    sprinter_namespace = None  # the namespace to make installs with. this affects:
    # the prefix added to injections
    last_phase = None  # the last phase run
    # a list of errors that occured within the environment's run.
    # an error should be a tuple with the source of the error and the description.
    errors = []

    def __init__(self, logger=None, logging_level=logging.INFO,
                 root=None, sprinter_namespace='sprinter'):
        self.system = System()
        if not logger:
            logger = self._build_logger(level=logging.INFO)
        self.logger = logger
        self.sprinter_namespace = sprinter_namespace
        self.root = root or os.path.expanduser(os.path.join("~", ".%s" % sprinter_namespace))
        if logging_level == logging.DEBUG:
            self.logger.info("Starting in debug mode...")

    @warmup
    def install(self):
        """ Install the environment """
        self.last_phase = "install"
        if not self.directory.new:
            self.logger.info("Namespace %s already exists!" % self.namespace)
            self.source = self.config.set_source(Manifest(self.directory.manifest_path))
            return self.update()
        try:
            self.logger.info("Installing environment %s..." % self.namespace)
            self.directory.initialize()
            self.install_sandboxes()
            self._specialize_contexts()
            for feature in self.config.installs():
                self.install_feature(feature)
            self.inject_environment_rc()
            self._finalize()
        except Exception, e:
            self.logger.error("An error occured during installation!")
            self.clear_environment_rc()
            self.logger.info("Removing installation %s..." % self.namespace)
            self.directory.remove()
            raise e
        
    @warmup
    @install_required
    def update(self, reconfigure=False):
        """ update the environment """
        self.last_phase = "update"
        self.logger.info("Updating environment %s..." % self.namespace)
        self.install_sandboxes()
        if reconfigure:
            self.config.grab_inputs(force_prompt=True)
        self._specialize_contexts()
        for feature in self.config.installs():
            self.install_feature(feature)
        for feature in self.config.updates():
            self.update_feature(feature)
        for feature in self.config.removes():
            self.remove_feature(feature)
        self.inject_environment_rc()
        self._finalize()

    @warmup
    @install_required
    def remove(self):
        """ remove the environment """
        self.last_phase = "remove"
        self.logger.info("Removing environment %s..." % self.namespace)
        self._specialize_contexts()
        for feature in self.config.removes():
            self.remove_feature(feature)
        self.clear_environment_rc()
        self.directory.remove()
        self.injections.commit()

    @warmup
    @install_required
    def deactivate(self):
        """ deactivate the environment """
        self.last_phase = "deactivate"
        self.logger.info("Deactivating environment %s..." % self.namespace)
        self.directory.rewrite_rc = False
        self._specialize_contexts()
        for feature in self.config.deactivations():
            self.deactivate_feature(feature)
        self.clear_environment_rc()
        self._finalize()

    @warmup
    @install_required
    def activate(self):
        """ activate the environment """
        self.last_phase = "activate"
        self.logger.info("Activating environment %s..." % self.namespace)
        self.directory.rewrite_rc = False
        self._specialize_contexts()
        for feature in self.config.activations():
            self.activate_feature(feature)
        self.inject_environment_rc()
        self._finalize()

    @warmup
    @install_required
    def reconfigure(self):
        """ reconfigure the environment """
        self.last_phase = "reconfigure"
        self.config.grab_inputs(force_prompt=True)
        if os.path.exists(self.directory.manifest_path):
            self.config.write(open(self.directory.manifest_path, "w+"))
        self.logger.info("Reconfigured! Note: It's recommended to update after a configure")

    @warmup
    @populate_formula_instance('target')
    def install_feature(self, feature_name, formula_instance=None):
        """ Install a specific formula """
        return self._run_action("Installing", feature_name, formula_instance.install, ['target'])

    @warmup
    @populate_formula_instance('target')
    def update_feature(self, feature_name, formula_instance=None):
        """ Update a specific formula """
        return self._run_action("Updating", feature_name, formula_instance.update, ['source', 'target'])

    @warmup
    @populate_formula_instance('source')
    def remove_feature(self, feature_name, formula_instance=None):
        """ Remove a specific formula """
        return self._run_action("Removing", feature_name, formula_instance.remove, ['source'])

    @warmup
    @populate_formula_instance('source')
    def deactivate_feature(self, feature_name, formula_instance=None):
        """ Deactivate a specific formula """
        return self._run_action("Deactivating", feature_name, formula_instance.deactivate, ['source'])

    @warmup
    @populate_formula_instance('source')
    def activate_feature(self, feature_name, formula_instance=None):
        """ Activate a specific formula """
        return self._run_action("Activating", feature_name, formula_instance.activate, ['source'])

    @warmup
    @populate_formula_instance('target')
    def validate_feature(self, feature_name, formula_instance=None):
        """ Validate a specific formula """
        return self._run_action("Activating", feature_name, formula_instance.activate, ['target'])

    @warmup
    def validate_manifest(self, manifest):
        """ Validate a manifest object """
        invalidations = manifest.invalidations
        for s in self.target.formula_sections():
            invalidations += self.validate_feature(self, s)
        return invalidations

    @warmup
    def inject_environment_rc(self):
        # clearing profile for now, to make sure
        # profile injections are cleared for sprinter installs
        self.injections.clear("~/.profile")
        self.injections.inject("~/.bash_profile", "[ -d %s ] && . %s/.rc" %
                               (self.directory.root_dir, self.directory.root_dir))
        self.injections.inject("~/.bashrc", "[ -d %s ] && . %s/.rc" %
                               (self.directory.root_dir, self.directory.root_dir))

    @warmup
    def clear_environment_rc(self):
        self.injections.clear("~/.profile")
        self.injections.clear("~/.bash_profile")
        self.injections.clear("~/.bashrc")

    def install_sandboxes(self):
        # install virtualenv
        if self.target:
            self._install_sandbox('virtualenv', virtualenv.create_environment,
                                  {'use_distribute': True})
            if self.system.isOSX():
                self._install_sandbox('brew', brew.install_brew)

    def write_debug_log(self, file_path):
        """ Write the debug log to a file """
        with open(file_path, "w+") as fh:
            fh.write(self._debug_stream.getvalue())

    def message_failure(self):
        """ return a failure message, if one exists """
        manifest = self.target or self.source
        if manifest.has_option('config', 'message_failure'):
            return manifest.get('config', 'message_failure')
        return None

    def message_success(self):
        """ return a success message, if one exists """
        manifest = self.target or self.source
        if manifest.has_option('config', 'message_success'):
            return manifest.get('config', 'message_success')

    def _warmup(self):
        """ initialize variables necessary to perform a sprinter action """
        self.logger.debug("Warming up...")
        try:
            if not isinstance(self.source, Manifest) and self.source:
                self.source = Manifest(self.source)
            if not isinstance(self.target, Manifest) and self.target:
                self.target = Manifest(self.target)
        except self.lib.BadCredentialsException, e:
            self.logger.error(str(e))
            raise SprinterException("Fatal error! Bad credentials to grab manifest!")
        self.config = Config(source=self.source, target=self.target,
                             namespace=self.namespace)
        if not self.namespace:
            self.namespace = self.config.namespace
        if not self.directory:
            self.directory = Directory(self.namespace, sprinter_root=self.root)
        self.injections = Injections(wrapper="%s_%s" % (self.sprinter_namespace.upper(), self.namespace))
        # append the bin, in the case sandboxes are necessary to
        # execute commands further down the sprinter lifecycle
        os.environ['PATH'] = self.directory.bin_path() + ":" + os.environ['PATH']
        self.warmed_up = True

    def _finalize(self):
        """ command to run at the end of sprinter's run """
        self.logger.info("Finalizing...")
        if os.path.exists(self.directory.manifest_path):
            self.config.write(open(self.directory.manifest_path, "w+"))
        if self.directory.rewrite_rc:
            self.directory.add_to_rc("export PATH=%s:$PATH" % self.directory.bin_path())
            self.directory.add_to_rc("export LIBRARY_PATH=%s:$LIBRARY_PATH" % self.directory.lib_path())
            self.directory.add_to_rc("export C_INCLUDE_PATH=%s:$C_INCLUDE_PATH" % self.directory.include_path())
        self.injections.commit()
        if self.message_success():
            self.logger.info(self.message_success())

    def _install_sandbox(self, name, call, kwargs={}):
        if (self.target.is_true('config', name) and
           (not self.source or not self.source.is_true('config', name))):
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

    def _get_formula_instance(self, formula):
        """
        get an instance of the formula object object if it exists, else
        create one, add it to the dict, and pass return it.
        """
        return get_formula_class(formula, self)

    def _run_action(self, verb, feature_name, call, configs):
        self.logger.info("%s %s..." % (verb, feature_name))
        configs = [getattr(self.config, c).get_feature_config(feature_name) for c in configs]
        valid = True
        for c in configs:
            if 'formula' not in c:
                valid = False
        if valid:
            call(feature_name, *configs)
        else:
            self.logger.warn("Feature %s has invalid configs! Not %s" % (feature_name, verb))

    def _specialize_contexts(self):
        """ Add variables and specialize contexts """
        # add in the 'root_dir' directories to the context dictionaries
        self.config.grab_inputs()
        for manifest in [self.source, self.target]:
            context_dict = {}
            if manifest:
                for s in manifest.formula_sections():
                    context_dict["%s:root_dir" % s] = self.directory.install_directory(s)
                    context_dict['config:root_dir'] = self.directory.root_dir
                    context_dict['config:node'] = self.system.node
                manifest.add_additional_context(context_dict)
