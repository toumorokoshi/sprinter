from __future__ import unicode_literals
import logging
import os.path
from mock import patch
from sprinter.testtools import FormulaTest
import sprinter.lib as lib

vals = {
    'repoA': 'git://github.com/toumorokoshi/sprinter.git'
}

source_config = """
[update]
formula = sprinter.formula.git
url = %(repoA)s
""" % vals

target_config = """
[simple_example]
formula = sprinter.formula.git
url = %(repoA)s

[update]
formula = sprinter.formula.git
url = %(repoA)s
branch = develop
""" % vals


class TestGitFormula(FormulaTest):
    """ Tests for the git formula """

    def setup(self):
        super(TestGitFormula, self).setup(source_config=source_config,
                                          target_config=target_config)
        self.curdir = os.path.abspath(os.curdir)

    def teardown(self):
        os.chdir(self.curdir)

    @patch.object(lib, 'call')
    def test_simple_example(self, call):
        """ The git formula should call a clone to a git repo """
        call.return_value = (0, '')
        self.environment.run_feature('simple_example', 'sync')
        call.assert_called_with("git clone %s %s" % (vals['repoA'],
                                                     self.directory.install_directory('simple_example')),
                                output_log_level=logging.DEBUG)

    @patch.object(lib, 'call')
    def test_update(self, call_mock):
        """ The git formula should call a clone to a git repo """
        call_mock.return_value = (0, '')
        self.environment.run_feature('update', 'sync')
        call_mock.assert_any_call("git fetch origin develop", output_log_level=logging.DEBUG)
        call_mock.assert_any_call("git checkout develop", output_log_level=logging.DEBUG)
