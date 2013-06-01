from StringIO import StringIO

from nose import tools
from mock import Mock, call

from sprinter.manifest import Config, ConfigException, Manifest, ManifestException

manifest_correct_dependency = """
[sub]
formula = sprinter.formulas.git
depends = git
url = git://github.com/Toumorokoshi/sub.git
branch = yusuke
rc = temp=`pwd`; cd %(sub:root_dir)s/libexec && . sub-init2 && cd $tmp

[git]
formula = sprinter.formulas.package
apt-get = git-core
brew = git
"""

manifest_incorrect_dependency = """
[config]
namespace = sprinter

[sub]
formula = sprinter.formulas.git
depends = sub
"""


test_input_string = \
"""
gitroot==~/workspace
username
password?
main_branch==comp_main
"""


class TestManifest(object):
    """
    Tests the Manifest object
    """

    def setup(self):
        self.manifest_old = Manifest(StringIO(manifest_old))
        self.manifest_incorrect_dependency = Manifest(StringIO(manifest_incorrect_dependency))

    def test_dependency_order(self):
        """ Test whether a proper dependency tree generated the correct output. """
        sections = self.manifest_old.formula_sections()
        assert sections.index('git') < sections.index('sub'), \
            "Dependency is out of order! git comes after sub"

    def test_incorrect_dependency(self):
        """ Test whether an incorrect dependency tree returns an error. """
        assert len(self.manifest_incorrect_dependency.invalidations) > 0, \
            "No errors were produced with an incorrect manifest"

    @tools.raises(ManifestException)
    def test_formula_class_bad_name(self):
        """ Getting a feature that doesn't exist should raise an exception """
        self.manifest_old.get_feature_class('febetnaetnuh')

    def test_equality(self):
        """ Manifest object should be equal to itself """
        tools.eq_(self.manifest_old, Manifest(StringIO(manifest_old)))

manifest_old = """
[config]
namespace = sprinter

[maven]
formula = sprinter.formulas.unpack
specific_version = 2.10

[ant]
formula = sprinter.formulas.unpack
specific_version = 1.8.4

[sub]
formula = sprinter.formulas.git
depends = git
url = git://github.com/Toumorokoshi/sub.git
branch = yusuke
rc = temp=`pwd`; cd %(sub:root_dir)s/libexec && . sub-init2 && cd $tmp

[mysql]
formula = sprinter.formulas.package
apt-get = libmysqlclient
          libmysqlclient-dev
brew = mysql

[git]
formula = sprinter.formulas.package
apt-get = git-core
brew = git
"""

manifest_new = """
[config]
namespace = sprinter
inputs = gitroot==~/workspace
         username
         password?
         main_branch?==comp_main

[maven]
formula = sprinter.formulas.unpack
specific_version = 3.0.4

[ant]
formula = sprinter.formulas.unpack
specific_version = 1.8.4

[myrc]
formula = sprinter.formulas.template
"""


class TestConfig(object):
    """
    Test the Config object
    """

    def setup(self):
        self.old_manifest = Manifest(StringIO(manifest_old))
        self.new_manifest = Manifest(StringIO(manifest_new))
        self.config = Config(source=self.old_manifest,
                             target=self.new_manifest)
        self.config_source_only = Config(source=self.old_manifest)
        self.config_target_only = Config(target=self.new_manifest)

    def test_setups(self):
        """ Test if setups returns the proper list """
        tools.eq_(set(self.config.setups()), set(['myrc']))

    @tools.raises(ConfigException)
    def test_setups_notarget(self):
        """ Test if setups returns the proper list """
        self.config_source_only.setups()

    def test_updates(self):
        """ Test if updates returns the proper list """
        tools.eq_(set(self.config.updates()), set(['maven', 'ant']))
    
    @tools.raises(ConfigException)
    def test_updates_notarget(self):
        """ Updates without a target should raise an exception """
        self.config_source_only.updates()

    @tools.raises(ConfigException)
    def test_updates_nosource(self):
        """ Updates without a source should raise an exception """
        self.config_source_only.updates()

    def test_removes(self):
        """ Test if removes returns the proper list """
        tools.eq_(set(self.config.removes()), set(['sub', 'mysql', 'git']))

    @tools.raises(ConfigException)
    def test_removes_nosource(self):
        """ Removes without a source should raise an exception """
        self.config_target_only.removes()

    def test_deactivations(self):
        """ Test if deactivations returns the proper list """
        tools.eq_(set(self.config.deactivations()), set(['maven', 'ant', 'sub', 'mysql', 'git']))

    @tools.raises(ConfigException)
    def test_deactivations_notsource(self):
        """ Deactivations without a source should raise an exception """
        self.config_target_only.deactivations()

    def test_activations(self):
        """ Test if deactivations returns the proper list """
        tools.eq_(set(self.config.activations()), set(['maven', 'ant', 'sub', 'mysql', 'git']))

    @tools.raises(ConfigException)
    def test_activations_notsource(self):
        """ Activations without a source should raise an exception """
        self.config_target_only.activations()

    def test_get_config(self):
        """ Test the get config """
        self.config.lib.prompt = Mock(return_value="no")
        self.config.get_config('hobopopo', default="Yes", secret=False)
        self.config.lib.prompt.assert_called_once_with("please enter your hobopopo",
                                                       default="Yes", secret=False)

    def test_grab_inputs(self):
        """ Test grabbing inputs """
        self.config.get_config = Mock()
        self.config.grab_inputs()
        self.config.get_config.has_calls([
            call("gitroot", default="~/workspace"),
            call("username"),
            call("password", secret=True),
            call("main_branch", default="comp_main", secret=True)
        ])

    def test_write(self):
        """ Test the write command """
        new_manifest = StringIO()
        self.config.write(new_manifest)
        tools.eq_(Manifest(new_manifest), Manifest(manifest_new))

    def test_write_with_temporary_config(self):
        """ The Write command with a temporary config value should not be written """
        self.config.lib.prompt = Mock(return_value="no")
        self.config.get_config('hobopopo', default="Yes", secret=False)
        new_manifest = StringIO()
        self.config.write(new_manifest)
        tools.eq_(Manifest(new_manifest), Manifest(manifest_new), "A secret value was written to the config!")

    def test_get_context_dict(self):
        """ Test getting a config dict """
        tools.eq_(self.config.get_context_dict(),
                  {'config:namespace': 'sprinter',
                   'config:hobopopo': 'no',
                   'maven:formula': 'sprinter.formulas.unpack',
                   'maven:specific_version': '3.0.4',
                   'ant:formula': 'sprinter.formulas.unpack',
                   'ant:specific_version': '1.8.4',
                   'myrc:formula': 'sprinter.formulas.template'})

    @tools.raises(ConfigException)
    def test_get_context_dict_bad_manifest_type(self):
        """ A band manifest type should raise an exception on get context dict """
        self.config.get_context_dict('hobo')
