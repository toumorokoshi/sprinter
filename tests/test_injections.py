import os
import shutil
import tempfile
import unittest

from sprinter.injections import Injections, sprinter_override_match


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
        self.assertTrue(l.find(test_injection) != -1, "Injection was not injected properly!")
        self.assertTrue(l.find(self.permenant_string) != -1, "Permanent string was removed on inject!")
        i.clear(self.temp_file_path)
        i.commit()
        l = open(self.temp_file_path, 'r').read()
        self.assertTrue(l.find(test_injection) == -1, "Injection was not cleared properly!")
        self.assertTrue(l.find(self.permenant_string) != -1, "Permanent string was removed on clear!")
