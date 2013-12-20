import httpretty
import os
import shutil
import tempfile
from mock import Mock, patch
from sprinter.testtools import FormulaTest
import sprinter.lib as lib

source_config = """
"""

target_config = """
[simple_example]
formula = sprinter.formula.template
source = %(temp_dir)s/in.txt
target = %(temp_dir)s/out.txt
"""


class TestSSHFormula(FormulaTest):
    """ Tests for the unpack formula """

    def setup(self):
        self.temp_dir = tempfile.mkdtemp()
        config_dict = {'temp_dir': self.temp_dir}
        super(TestSSHFormula, self).setup(source_config=(source_config % config_dict),
                                          target_config=(target_config % config_dict))

    def teardown(self):
        shutil.rmtree(self.temp_dir)

    def skip_simple_example(self):
        """ The template formula should grab a template and save it """
        with open(os.path.join(self.temp_dir, 'in.txt'), 'w+') as fh:
            fh.write(SIMPLE_TEMPLATE)
        self.environment.run_feature("simple_example", 'sync')
        out_file = os.path.join(self.temp_dir, 'out.txt')
        assert os.path.exists(out_file)
        assert open(out_file).read() == SIMPLE_TEMPLATE
