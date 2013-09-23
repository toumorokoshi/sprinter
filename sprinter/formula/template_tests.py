from __future__ import unicode_literals
import httpretty
import os
import shutil
import tempfile
from sprinter.testtools import FormulaTest

source_config = """
[update_example]
formula = sprinter.formula.template
source = %(temp_dir)s/in.txt
target = %(temp_dir)s/out.txt
"""

target_config = """
[simple_example]
formula = sprinter.formula.template
source = %(temp_dir)s/in.txt
target = %(temp_dir)s/out.txt

[http_example]
formula = sprinter.formula.template
source = http://testme.com/test.txt
target = %(temp_dir)s/out.txt

[update_example]
formula = sprinter.formula.template
source = %(temp_dir)s/in.txt
target = %(temp_dir)s/out.txt
on_update = true
"""


class TestUnpackFormula(FormulaTest):
    """ Tests for the unpack formula """

    def setup(self):
        self.temp_dir = tempfile.mkdtemp()
        config_dict = {'temp_dir': self.temp_dir}
        super(TestUnpackFormula, self).setup(source_config=(source_config % config_dict),
                                             target_config=(target_config % config_dict))

    def teardown(self):
        shutil.rmtree(self.temp_dir)

    def test_simple_example(self):
        """ The template formula should grab a template and save it """
        with open(os.path.join(self.temp_dir, 'in.txt'), 'w+') as fh:
            fh.write(SIMPLE_TEMPLATE)
        self.environment.run_feature("simple_example", 'sync')
        out_file = os.path.join(self.temp_dir, 'out.txt')
        assert os.path.exists(out_file)
        assert open(out_file).read() == SIMPLE_TEMPLATE
        
    @httpretty.activate
    def test_http_example(self):
        """ The template formula should grab a template via http and save it """
        TEST_URI = "http://testme.com/test.txt"
        httpretty.register_uri(httpretty.GET, TEST_URI,
                               body=SIMPLE_TEMPLATE)
        self.environment.run_feature("http_example", 'sync')
        out_file = os.path.join(self.temp_dir, 'out.txt')
        assert os.path.exists(out_file)
        assert open(out_file).read() == SIMPLE_TEMPLATE

    def test_update_example(self):
        """ The template formula should update a template when on_update is set """
        with open(os.path.join(self.temp_dir, 'in.txt'), 'w+') as fh:
            fh.write(UPDATE_TEMPLATE)
        self.environment.run_feature("update_example", 'sync')
        out_file = os.path.join(self.temp_dir, 'out.txt')
        assert os.path.exists(out_file)
        assert open(out_file).read() == UPDATE_TEMPLATE
        

SIMPLE_TEMPLATE = """
This is a simple template.
"""

UPDATE_TEMPLATE = """
This is an updated template.
"""
