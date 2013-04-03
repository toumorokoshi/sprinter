import os
import shutil
import tempfile
import unittest

from sprinter.injections import Injections

TEST_CONTENT = \
"""
Testing abc.

#OVERRIDE
here is an override string. it should appear at the bottom.
#OVERRIDE
"""

TEST_OVERRIDE_CONTENT = \
"""
Testing abc.


#testinjection
injectme
#testinjection

#OVERRIDE
here is an override string. it should appear at the bottom.
#OVERRIDE"""


class TestInjections(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.permenant_string = "this should stay no matter what."
        self.temp_file_path = os.path.join(self.temp_dir, "test")
        fh = open(self.temp_file_path, 'w+')
        fh.write(self.permenant_string)
        fh.close()

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_injection(self):
        """ Test a complete injection workflow """
        i = Injections("testinjection")
        test_injection = "this should stay temporarily"
        i.inject(self.temp_file_path, test_injection)
        i.commit()
        l = open(self.temp_file_path, 'r').read()
        self.assertTrue(l.count(test_injection) > 0, "Injection was not injected properly!")
        self.assertTrue(l.count(test_injection) == 1, "Multiple injections were found!")
        self.assertTrue(l.find(self.permenant_string) != -1, "Permanent string was removed on inject!")
        i.clear(self.temp_file_path)
        i.commit()
        l = open(self.temp_file_path, 'r').read()
        self.assertTrue(l.find(test_injection) == -1, "Injection was not cleared properly!")
        self.assertTrue(l.find(self.permenant_string) != -1, "Permanent string was removed on clear!")

    def test_override(self):
        """ Test the override functionality """
        i = Injections("testinjection", override="OVERRIDE")
        c = i.inject_content(TEST_CONTENT, "injectme")
        self.assertEqual(c, TEST_OVERRIDE_CONTENT, "Override result is different from expected.")

    def test_injected(self):
        """ Test the injected method to determine if a file has already been injected..."""
        i = Injections("testinjection")
        self.assertFalse(i.injected(self.temp_file_path), "Injected check returned true when not injected yet.")
        test_injection = "this should stay temporarily"
        i.inject(self.temp_file_path, test_injection)
        i.commit()
        self.assertTrue(i.injected(self.temp_file_path), "Injected check returned false")
