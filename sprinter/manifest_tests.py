from StringIO import StringIO

from nose import tools
from mock import Mock, call

from sprinter.manifest import Config, ConfigException, Manifest, ManifestException
from sprinter.system import System

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

test_input_string = """
gitroot==~/workspace
username
password?
main_branch==comp_main
"""

osx_only_manifest = """
[osx]
systems = osx
formula = sprinter.formulas.template

[osx2]
systems = OsX
formula = sprinter.formulas.template
"""

debian_only_manifest = """
[debian]
systems = debian
formula = sprinter.formulas.template

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

    def test_get_feature_class(self):
        """ Get Feature class should return the formula class name of the feature """
        tools.eq_(self.manifest_old.get_feature_class("sub"), "sprinter.formulas.git")

    @tools.raises(ManifestException)
    def test_feature_class_bad_name(self):
        """ Getting a feature that doesn't exist should raise an exception """
        self.manifest_old.get_feature_class('febetnaetnuh')

    def test_equality(self):
        """ Manifest object should be equal to itself """
        tools.eq_(self.manifest_old, Manifest(StringIO(manifest_old)))

    def test_get_feature_config(self):
        """ Get_feature_config should return a dictionary with the attributes """
        tools.eq_(self.manifest_old.get_feature_config("sub"), {
            'url': 'git://github.com/Toumorokoshi/sub.git',
            'formula': 'sprinter.formulas.git',
            'depends': 'git',
            'branch': 'yusuke',
            'rc': 'temp=`pwd`; cd %(sub:root_dir)s/libexec && . sub-init2 && cd $tmp',
            'bc': 'temp=`pwd`; cd %(sub:testvar)s/libexec && . sub-init2 && cd $tmp'})

    def test_get_context_dict(self):
        """ Test getting a config dict """
        context_dict = self.manifest_old.get_context_dict()
        test_dict = {'maven:formula': 'sprinter.formulas.unpack',
                     'config:hobopopo': 'no',
                     'maven:specific_version': '2.10',
                     'ant:formula': 'sprinter.formulas.unpack',
                     'mysql:formula': 'sprinter.formulas.package',
                     'sub:rc': 'temp=`pwd`; cd %(sub:root_dir)s/libexec && . sub-init2 && cd $tmp',
                     'ant:specific_version': '1.8.4',
                     'sub:formula': 'sprinter.formulas.git',
                     'sub:branch': 'yusuke',
                     'git:apt-get': 'git-core',
                     'sub:url': 'git://github.com/Toumorokoshi/sub.git',
                     'ant:phases': 'update',
                     'sub:depends': 'git',
                     'config:namespace': 'sprinter',
                     'sub:bc': 'temp=`pwd`; cd %(sub:testvar)s/libexec && . sub-init2 && cd $tmp',
                     'mysql:apt-get': 'libmysqlclient\nlibmysqlclient-dev',
                     'config:username': 'toumorokoshi',
                     'config:gitroot': '~/workspace',
                     'mysql:brew': 'mysql',
                     'git:brew': 'git',
                     'git:formula': 'sprinter.formulas.package',
                     'config:test_variable': 'test',
                     'config:inputs': 'sourceonly'}
        for k, v in test_dict.items():
            tools.eq_(context_dict[k], v)
        self.manifest_old.add_additional_context({"config:test": "testing this"})
        assert "config:test" in self.manifest_old.get_context_dict()

    def test_get_context_dict_escaped_character(self):
        """ Test getting a config dict with escaping filter will properly escape a character"""
        manifest = Manifest(StringIO(manifest_escaped_parameters))
        context_dict = manifest.get_context_dict()
        assert "section:escapeme|escaped" in context_dict
        tools.eq_(context_dict["section:escapeme|escaped"], "\!\@\#\$\%\^\&\*\(\)\\\"\\'\~\`\/\?\<\>")

    def test_run_phase(self):
        """
        Run phase should allow phases that are specifically listed, and
        disallow ones that are not
        """
        assert self.manifest_old.run_phase('ant', 'update'), \
            "Update in phase but not being run!"
        assert not self.manifest_old.run_phase('ant', 'install'), \
            "Install not in phase but being run!"
        assert self.manifest_old.run_phase('sub', 'deactivate'), \
            "Deactivate not run in feature that does not specify phase!"

    def test_osx_only(self):
        """ Test a feature that should only occur on osx """
        test_manifest = Manifest(StringIO(osx_only_manifest))
        test_manifest.system = Mock()
        test_manifest.system.isOSX = Mock(return_value=True)
        assert test_manifest.run_phase('osx', 'install')
        assert test_manifest.run_phase('osx2', 'install')
        test_manifest.system.isOSX = Mock(return_value=False)
        assert not test_manifest.run_phase('osx', 'install')
        assert not test_manifest.run_phase('osx2', 'install')

    def test_debianbased_only(self):
        """ Test a feature that should only occur on debian-based distributions """
        test_manifest = Manifest(StringIO(debian_only_manifest))
        test_manifest.system = Mock(spec=System)
        test_manifest.system.isDebianBased = Mock(return_value=True)
        assert test_manifest.run_phase('debian', 'install')
        test_manifest.system.isDebianBased = Mock(return_value=False)
        assert not test_manifest.run_phase('debian', 'install')
        assert not test_manifest.run_phase('debian', 'update')

    def test_add_additional_context(self):
        """ Test the add additonal context method """
        self.manifest_old.add_additional_context({'testme': 'testyou'})
        assert 'testme' in self.manifest_old.additional_context_variables
        self.manifest_old.add_additional_context({'testhim': 'testher'})
        assert 'testme' in self.manifest_old.additional_context_variables
        assert 'testhim' in self.manifest_old.additional_context_variables


manifest_old = """
[config]
namespace = sprinter
inputs = sourceonly

[maven]
formula = sprinter.formulas.unpack
specific_version = 2.10

[ant]
formula = sprinter.formulas.unpack
phases = update
specific_version = 1.8.4

[sub]
formula = sprinter.formulas.git
depends = git
url = git://github.com/Toumorokoshi/sub.git
branch = yusuke
rc = temp=`pwd`; cd %(sub:root_dir)s/libexec && . sub-init2 && cd $tmp
bc = temp=`pwd`; cd %(sub:testvar)s/libexec && . sub-init2 && cd $tmp

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

manifest_input_params = """
[config]
namespace = sprinter
username = toumorokoshi
gitroot = ~/workspace
"""

manifest_escaped_parameters = """
[section]
namespace = sprinter
username = toumorokoshi
gitroot = ~/workspace
escapeme = !@#$%^&*()"'~`/?<>
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

    def test_intalls(self):
        """ Test if setups returns the proper list """
        tools.eq_(set(self.config.installs()), set(['myrc']))

    @tools.raises(ConfigException)
    def test_setups_notarget(self):
        """ Test if setups returns the proper list """
        self.config_source_only.installs()

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
        tools.eq_(set(self.config.deactivations()), set(['maven', 'sub', 'mysql', 'git']))

    @tools.raises(ConfigException)
    def test_deactivations_notsource(self):
        """ Deactivations without a source should raise an exception """
        self.config_target_only.deactivations()

    def test_activations(self):
        """ Test if deactivations returns the proper list """
        tools.eq_(set(self.config.activations()), set(['maven', 'sub', 'mysql', 'git']))

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
        self.config.get_config.assert_has_calls([
            call("gitroot", default="~/workspace", secret=False),
            call("username", default=None, secret=False),
            call("password", default=None, secret=True),
            call("main_branch", default="comp_main", secret=True)
        ])

    def test_grab_inputs_existing_source(self):
        """ Grabbing inputs should source from source first, if it exists """
        source_manifest = Manifest(StringIO(manifest_input_params))
        config = Config(source=source_manifest,
                        target=self.new_manifest)
        config.get_config = Mock()
        config.grab_inputs()
        config.get_config.assert_has_calls([
            call("password", default=None, secret=True),
            call("main_branch", default="comp_main", secret=True)
        ])
        assert config.get_config.call_count == 2, "More calls were called!"

    def test_grab_inputs_additional_context(self):
        """ Grab inputs should re-call additional context """
        source_manifest = Manifest(StringIO(manifest_input_params))
        config = Config(source=source_manifest,
                        target=self.new_manifest)
        config.get_config = Mock()
        config.grab_inputs()
        assert 'config:username' in config.source.additional_context_variables,\
            "Username config not added to context variables!"
        
    def test_grab_inputs_source(self):
        """ Test grabbing inputs from source """
        self.config_source_only.get_config = Mock(return_value="no")
        self.config_source_only.grab_inputs()
        self.config_source_only.get_config.assert_called_once_with(
            "sourceonly", default=None, secret=False)

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

    @tools.raises(ConfigException)
    def test_set_additional_context_bad_manifest_type(self):
        """ A band manifest type should raise an exception on get context dict """
        self.config.set_additional_context('hobo')
        
    def test_additional_context(self):
        """ Ensure that additional context variables are configured correctly """
        additional_context_variables = {"sub:root_dir": "teststring"}
        self.config.set_additional_context('source', additional_context_variables)
        sub_values = self.config.source.get_feature_config("sub")
        assert sub_values['rc'].find("teststring") != -1, "teststring is not substituted in"
        # should add to context
        additional_context_variables = {"sub:testvar": "teststring2"}
        self.config.set_additional_context('source', additional_context_variables)
        sub_values = self.config.source.get_feature_config("sub")
        assert sub_values['rc'].find("teststring") != -1, "teststring is not substituted in"
        assert sub_values['bc'].find("teststring2") != -1, "teststring2 is not substituted in"

    def test_set_source(self):
        """ Test the source set """
        self.config.config['test_variable'] = "test"
        source = Manifest(manifest_old)
        self.config.set_source(source)
        assert 'config:test_variable' in source.additional_context_variables,\
            "Additional context variables not set on new source!"
