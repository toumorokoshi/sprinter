"""
Tests for the command line interface
"""
import unittest
import logging
import tempfile
import shutil
import os
from mock import call, Mock, patch

from sprinter.install import parse_args
from . import TEST_MANIFEST

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
        args = ['install', 'http://www.google.com']
        calls = [call(logging_level=logging.INFO),
                 call().install('http://www.google.com',
                                username=None,
                                password=None,
                                namespace=None)]
        parse_args(args, Environment=environment)
        environment.assert_has_calls(calls)

    @patch('sprinter.environment.Environment')
    def test_errors_(self, environment):
        config = {'validate_manifest.return_value' : ['this is funky']}
        environment.configure_mock(**config)
        args = ['validate', self.temp_file_path]
        calls = [call(logging_level=logging.INFO),
                 call().validate_manifest(self.temp_file_path,
                                username=None,
                                password=None)]
        parse_args(args, Environment=environment)
        environment.assert_has_calls(calls)
