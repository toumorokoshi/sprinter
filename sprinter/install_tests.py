"""
Tests for the command line interface
"""
import unittest
import logging
import tempfile
import shutil
import os
from mock import call, patch

from sprinter.install import parse_args, parse_domain

TEST_MANIFEST = \
    """
[config]
inputs = stashroot==~/p4
         username
         password?
         main_branch==comp_main
[sub]
recipe = sprinter.recipes.git
url = git://github.com/Toumorokoshi/sub.git
branch = yusuke
rc = temp=`pwd`; cd %(sub:root_dir)s/libexec && . sub-init2 && cd $tmp
[m2]
recipe = sprinter.recipes.template
target = ~/.m2/settings.bak
source = https://raw.github.com/Toumorokoshi/EmacsEnv/master/.vimrc
[perforce]
inputs = p4passwd?
recipe = sprinter.recipes.perforce
version = r10.1
username = %(config:username)
password = %(config:p4passwd)
client = perforce.local:1666
"""


class TestInstall(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.temp_file_path = os.path.join(self.temp_dir, "test.cfg")
        fh = open(self.temp_file_path, 'w+')
        fh.write(TEST_MANIFEST)
        fh.close()

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    @patch('sprinter.environment.Environment')
    def test_install_environment(self, environment):
        """ Test if install calls the proper methods """
        args = ['install', 'http://www.google.com']
        calls = [call(logging_level=logging.INFO),
                 call().install()]
        parse_args(args, Environment=environment)
        environment.assert_has_calls(calls)

    @patch('sprinter.environment.Environment')
    def test_errors(self, environment):
        """ Test if validate catches an invalid manifest """
        config = {'validate_manifest.return_value': ['this is funky']}
        environment.configure_mock(**config)
        args = ['validate', self.temp_file_path]
        calls = [call(logging_level=logging.INFO),
                 call().validate()]
        parse_args(args, Environment=environment)
        environment.assert_has_calls(calls)

    def test_parse_domain(self):
        """ Test if domains are properly parsed """
        match_tuples = [
            ("http://github.com/antehuantuehton", "http://github.com/"),
            ("https://github.com", "https://github.com")
        ]
        for in_string, out_string in match_tuples:
            self.assertEqual(parse_domain(in_string), out_string,
                             "%s did not result in %s! Resulted in %s instead."
                             % (in_string, out_string, parse_domain(in_string)))
