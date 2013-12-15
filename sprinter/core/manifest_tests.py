from __future__ import unicode_literals
from six import StringIO

import os
import httpretty
import tempfile
from nose import tools
from mock import Mock, call, patch

from sprinter.manifest import Manifest, ManifestException
import sprinter.lib as lib

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

http_manifest = """
[sub]
formula = sprinter.formulas.git
"""


class TestManifest(object):
    """
    Tests the Manifest object
    """

    def setup(self):
        self.old_manifest = Manifest(StringIO(old_manifest))
        self.new_manifest = Manifest(StringIO(new_manifest))

    def test_dependency_order(self):
        """ Test whether a proper dependency tree generated the correct output. """
        sections = self.old_manifest.formula_sections()
        assert sections.index('git') < sections.index('sub'), \
            "Dependency is out of order! git comes after sub"

    @tools.raises(ManifestException)
    def test_incorrect_dependency(self):
        """ Test whether an incorrect dependency tree returns an error. """
        Manifest(StringIO(manifest_incorrect_dependency))

    def test_equality(self):
        """ Manifest object should be equal to itself """
        tools.eq_(self.old_manifest, Manifest(StringIO(old_manifest)))

    def test_get_feature_config(self):
        """ get_feature_config should return a dictionary with the attributes """
        tools.eq_(self.old_manifest.get_feature_config("sub").to_dict(), {
            'url': 'git://github.com/Toumorokoshi/sub.git',
            'formula': 'sprinter.formulas.git',
            'depends': 'git',
            'branch': 'yusuke',
            'rc': 'temp=`pwd`; cd %(sub:root_dir)s/libexec && . sub-init2 && cd $tmp',
            'bc': 'temp=`pwd`; cd %(sub:testvar)s/libexec && . sub-init2 && cd $tmp'})

    def test_get_context_dict(self):
        """ Test getting a config dict """
        context_dict = self.old_manifest.get_context_dict()
        test_dict = {'maven:formula': 'sprinter.formulas.unpack',
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
                     'mysql:brew': 'mysql',
                     'git:brew': 'git',
                     'git:formula': 'sprinter.formulas.package',
                     'config:inputs': 'sourceonly'}
        for k, v in test_dict.items():
            tools.eq_(context_dict[k], v)
        self.old_manifest.add_additional_context({"config:test": "testing this"})
        assert "config:test" in self.old_manifest.get_context_dict()

    def test_get_context_dict_escaped_character(self):
        """ Test getting a config dict with escaping filter will properly escape a character"""
        manifest = Manifest(StringIO(manifest_escaped_parameters))
        context_dict = manifest.get_context_dict()
        assert "section:escapeme|escaped" in context_dict
        tools.eq_(context_dict["section:escapeme|escaped"], "\!\@\#\$\%\^\&\*\(\)\\\"\\'\~\`\/\?\<\>")

    def test_add_additional_context(self):
        """ Test the add additonal context method """
        self.old_manifest.add_additional_context({'testme': 'testyou'})
        assert 'testme' in self.old_manifest.additional_context_variables
        self.old_manifest.add_additional_context({'testhim': 'testher'})
        assert 'testme' in self.old_manifest.additional_context_variables
        assert 'testhim' in self.old_manifest.additional_context_variables

    @httpretty.activate
    def test_source_from_url(self):
        """ When the manifest is sourced from a url, the source should be the url. """
        TEST_URI = "http://testme.com/test.cfg"
        httpretty.register_uri(httpretty.GET, TEST_URI,
                               body=http_manifest)
        m = Manifest(TEST_URI)
        assert m.source() == TEST_URI

    @patch.object(lib, 'prompt')
    def test_get_config(self, prompt):
        """ Test the get config """
        prompt.return_value = "no"
        self.new_manifest.get_config('hobopopo', default="Yes", secret=False)
        prompt.assert_called_once_with("please enter your hobopopo",
                                       default="Yes", secret=False)

    @patch.object(lib, 'prompt')
    def test_get_config_force_prompt(self, prompt):
        """ Test the get config with force_prompt """
        prompt.return_value = "no"
        self.new_manifest.set('config', 'hobopopo', 'test')
        self.new_manifest.get_config('hobopopo', default="Yes", secret=False, force_prompt=True)
        prompt.assert_called_once_with("please enter your hobopopo",
                                       default="Yes", secret=False)

    def test_grab_inputs(self):
        """ Test grabbing inputs """
        self.new_manifest.get_config = Mock()
        self.new_manifest.grab_inputs()
        self.new_manifest.get_config.assert_has_calls([
            call("gitroot", default="~/workspace", secret=False, force_prompt=False),
            call("username", default=None, secret=False, force_prompt=False),
            call("password", default=None, secret=True, force_prompt=False),
            call("main_branch", default="comp_main", secret=True, force_prompt=False)
        ])

    def test_force_prompt_grab_inputs(self):
        """ Test the force_prompt grabbing of inputs """
        target = Manifest(StringIO(manifest_force_inputs))
        target.get_config = Mock()
        target.grab_inputs(force_prompt=True)
        target.get_config.assert_has_calls([
            call("gitroot", default="~/workspace", secret=False, force_prompt=True),
            call("username", default=None, secret=False, force_prompt=True),
            call("main_branch", default="comp_main", secret=True, force_prompt=True)
        ])

    def test_write(self):
        """ Test the write command """
        temp_file = tempfile.mkstemp()[1]
        try:
            with open(temp_file, 'w+') as fh:
                self.new_manifest.write(fh)
            tools.eq_(self.new_manifest, Manifest(temp_file))
        finally:
            os.unlink(temp_file)
        
    @patch.object(lib, 'prompt')
    def test_write_with_temporary_config(self, prompt):
        """ The Write command with a temporary config value should not be written """
        prompt.return_value = "no"
        self.new_manifest.get_config('hobopopo', default="Yes", secret=False)
        new_manifest = StringIO()
        self.new_manifest.write(new_manifest)
        assert not Manifest(new_manifest).has_option('config', 'hobopopo'), \
            "A secret value was written to the config!"
        
    @tools.raises(ManifestException)
    def test_invalid_manifest_filepath(self):
        """ The manifest should throw an exception on an invalid manifest path """
        Manifest("./ehiiehaiehnatheita")

old_manifest = """
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


new_manifest = """
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

manifest_force_inputs = """
[config]
namespace = sprinter
inputs = gitroot==~/workspace
         username
         main_branch?==comp_main
username = toumorokoshi
gitroot = ~/workspace
main_branch = comp_rel_a
"""
