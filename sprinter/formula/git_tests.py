import logging
from mock import Mock
from sprinter.testtools import FormulaTest
from nose.plugins.attrib import attr

vals = {
    'repoA': 'git://github.com/toumorokoshi/sprinter.git'
}

source_config = """
""" % vals

target_config = """
[simple_example]
formula = sprinter.formulas.git
url = %(repoA)s
""" % vals


class TestGitFormula(FormulaTest):
    """ Tests for the git formula """

    def setup(self):
        super(TestGitFormula, self).setup(source_config=source_config,
                                          target_config=target_config)

    def test_simple_example(self):
        """ The git formula should call a clone to a git repo """
        self.lib.call = Mock(return_value=(0, ''))
        self.environment.install_feature("simple_example")
        self.lib.call.assert_called_with("git clone %s %s" % (vals['repoA'],
                                                              self.directory.install_directory('simple_example')),
                                         output_log_level=logging.DEBUG)


@attr('full')
class TestAllGitFormula(FormulaTest):
    """ More, slower complete workflow tests for the git formula """
    def setup(self):
        super(TestGitFormula, self).setup(source_config=source_config,
                                          target_config=target_config)
