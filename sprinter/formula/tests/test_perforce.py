from __future__ import unicode_literals
import tempfile
import shutil
from mock import Mock, patch
from nose.tools import ok_
from nose.plugins.attrib import attr
from sprinter.testtools import FormulaTest, set_os_types
import sprinter.lib as lib

source_config = """
"""

target_config = """
[install]
formula = sprinter.formula.perforce
version = r10.1
root_path = {tmpdir}
username = username
password = password
port = perforce.local:1666
client = test_client
write_p4settings = true
write_password_p4settings = true
overwrite_p4settings = false
overwrite_client = false
"""


class TestPerforceFormula(FormulaTest):
    """
    Tests for the command formula.
    """
    def setup(self):
        self.temp_dir = tempfile.mkdtemp()
        super(TestPerforceFormula, self).setup(
            source_config=source_config,
            target_config=target_config.format(
                tmpdir=self.temp_dir
            )
        )

    def teardown(self):
        del(self.environment)
        shutil.rmtree(self.temp_dir)

    @attr('full')
    def test_install(self):
        with patch('sprinter.lib.extract_targz') as extract_targz:
            with set_os_types(debian=True):
                with patch('sprinter.lib.call') as call:
                    self.environment.run_feature("install", 'sync')
                    ok_(extract_targz.called)
                    # ok_(call.called)
