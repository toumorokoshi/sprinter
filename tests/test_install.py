"""
Tests for the command line interface
"""
import unittest
import logging
from mock import call, Mock, patch

from sprinter.install import parse_args


class TestInstall(unittest.TestCase):

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
