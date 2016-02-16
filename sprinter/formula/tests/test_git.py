from __future__ import unicode_literals
import logging
import os
import os.path
from mock import patch, call
from sprinter.testtools import FormulaTest
import sprinter.lib as lib
from sprinter.formula.git import CURRENT_REMOTE, CURRENT_BRANCH, CLONE_REPO, CHECKOUT_BRANCH, FETCH_BRANCH, MERGE_BRANCH, UPDATE_ORIGIN

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
    def test_simple_example(self, call_mock):
        """ The git formula should call a clone to a git repo """
        install_directory = self.directory.install_directory('simple_example')
        call_mock.return_value = (0, '')
        self.environment.run_feature('simple_example', 'sync')
        call_mock.assert_has_calls([
            call(CLONE_REPO.format(
                repo=vals['repoA'],
                dir=install_directory
            ), output_log_level=logging.DEBUG)
        ])

    @patch.object(lib, 'call')
    def test_update_different_branches(self, call_mock):
        """ The git formula should call checkout if target branch is not the current branch """
        install_directory = self.directory.install_directory('update')
        os.makedirs(install_directory)
        call_count = 0
        return_values = {
            CURRENT_REMOTE.format(dir=install_directory):
                'git://github.com/toumorokoshi/sprinter.git',
            CURRENT_BRANCH.format(dir=install_directory):
                'master'
        }
        call_mock.side_effect = lambda cmd, **kw: (0, return_values[cmd] if cmd in return_values else '')
        self.environment.run_feature('update', 'sync')
        call_mock.assert_any_call(
            FETCH_BRANCH.format(dir=install_directory, branch='develop'),
            output_log_level=logging.DEBUG
        )
        call_mock.assert_any_call(
            CHECKOUT_BRANCH.format(dir=install_directory, branch='develop'),
            output_log_level=logging.DEBUG
        )

    @patch.object(lib, 'call')
    def test_update_no_directory(self, call_mock):
        """ The git formula should re-clone a repo if the repo directory doesn't exist """
        call_mock.return_value = (0, 'git://github.com/toumorokoshi/sprinter.git')
        self.environment.run_feature('update', 'sync')
        call_mock.assert_any_call(
            CLONE_REPO.format(
                repo=vals['repoA'],
                dir=self.directory.install_directory('update')),
            output_log_level=logging.DEBUG)
