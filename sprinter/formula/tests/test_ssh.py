from __future__ import unicode_literals
import httpretty
import os
import shutil
import tempfile
from mock import Mock, patch
from nose.tools import ok_
from sprinter.testtools import FormulaTest
import sprinter.lib as lib

source_config = """
"""

target_config = """
[github]
formula = sprinter.formula.ssh
host = github.com
keyname = github
nopassphrase = true
type = rsa
hostname = github.com
user = toumorokoshi
create = false
use_global_ssh = yes

[port]
formula = sprinter.formula.ssh
host = github.com
keyname = github
nopassphrase = true
type = rsa
hostname = github.com
user = toumorokoshi
create = false
port = 4444
use_global_ssh = no
"""


class TestSSHFormula(FormulaTest):
    """ Tests for the unpack formula """

    def setup(self):
        super(TestSSHFormula, self).setup(source_config=source_config,
                                          target_config=target_config)

    def test_use_global_ssh(self):
        """ If use_global_ssh is false, then no config should be injected into ssh config"""
        self.environment.injections.inject = Mock()
        self.environment.run_feature("github", "sync")
        ok_(not self.environment.injections.inject.called)

    def test_use_port_ssh(self):
        """ If port is included, port should be injected in the ssh config """
        self.environment.injections.inject = Mock()
        self.environment.run_feature("port", "sync")
        ok_("Port 4444" in self.environment.injections.inject.call_args[0][1])
