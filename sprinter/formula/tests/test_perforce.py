import tempfile
import shutil
from mock import Mock, patch
from sprinter.testtools import FormulaTest
import sprinter.lib as lib

source_config = """
"""

target_config = """
[install]
formula = sprinter.formula.perforce
version = r10.1
root_path = %(root_path)s
username = username
password = password
port = perforce.local:1666
client = test_client
write_p4settings
write_password_p4settings = true
overwrite_p4settings = false
overwrite_client = false
"""


class TestPerforceFormula(FormulaTest):
    """
    Tests for the command formula.
    """
    def setup(self):
        super(TestPerforceFormula, self).setup(source_config=source_config,
                                               target_config=target_config)
        self.temp_dir = tempfile.mkdtemp()

    def teardown(self):
        del(self.environment)
        shutil.rmtree(self.temp_dir)
        
    """
    @patch.object(lib, 'call')
    def test_install(self, call):
        self.environment.run_feature("install", 'sync')
    """
