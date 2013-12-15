import os
import shutil
import tempfile

from sprinter.core.injections import Injections

TEST_CONTENT = """
Testing abc.

#OVERRIDE
here is an override string. it should appear at the bottom.
#OVERRIDE
"""

TEST_OVERRIDE_CONTENT = """
Testing abc.

#testinjection
injectme
#testinjection

#OVERRIDE
here is an override string. it should appear at the bottom.
#OVERRIDE
"""


class TestInjections(object):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.permanent_string = "this should stay no matter what."
        self.test_injection = "this should stay temporarily"
        self.temp_file_path = os.path.join(self.temp_dir, "test")
        fh = open(self.temp_file_path, 'w+')
        fh.write(self.permanent_string)
        fh.close()

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_injection(self):
        """ Test a complete injection workflow """
        i = Injections("testinjection")
        i.inject(self.temp_file_path, self.test_injection)
        i.commit()
        l = open(self.temp_file_path, 'r').read()
        assert l.count(self.test_injection) > 0, "Injection was not injected properly!"
        assert l.count(self.test_injection) == 1, "Multiple injections were found!"
        assert l.find(self.permanent_string) != -1, "Permanent string was removed on inject!"
        i.clear(self.temp_file_path)
        i.commit()
        l = open(self.temp_file_path, 'r').read()
        assert l.find(self.test_injection) == -1, "Injection was not cleared properly!"
        assert l.find(self.permanent_string) != -1, "Permanent string was removed on clear!"

    def test_similar_injectionname(self):
        # and add in the originally named injection
        i = Injections("testinjection")
        i.inject(self.temp_file_path, self.test_injection)
        i.commit()
        # start with a similar injection
        SIMILAR_INJECTION = "This is a similar injection"
        i_similiar = Injections("testinjectionsagain")
        i_similiar.inject(self.temp_file_path, SIMILAR_INJECTION)
        i_similiar.commit()
        l = open(self.temp_file_path, 'r').read()
        assert l.count(SIMILAR_INJECTION) > 0, "Similar injection was removed!"
        assert l.count(SIMILAR_INJECTION) == 1, "Multiple injections were found!"
        i.clear(self.temp_file_path)
        i.commit()
        l = open(self.temp_file_path, 'r').read()
        assert l.find(self.test_injection) == -1, "Injection was not cleared properly!"
        assert l.find(SIMILAR_INJECTION) > 0, "Similar Injection was incorrectly cleared!"

    def test_override(self):
        """ Test the override functionality """
        i = Injections("testinjection", override="OVERRIDE")
        c = i.inject_content(TEST_CONTENT, "injectme")
        assert c == TEST_OVERRIDE_CONTENT, "Override result is different from expected."

    def test_injected(self):
        """ Test the injected method to determine if a file has already been injected..."""
        i = Injections("testinjection")
        assert not i.injected(self.temp_file_path), "Injected check returned true when not injected yet."
        i.inject(self.temp_file_path, self.test_injection)
        i.commit()
        assert i.injected(self.temp_file_path), "Injected check returned false"

    def test_in_noninjected_file(self):
        """
        in_noninjected_file should return true if a string exists
        non-injected and false it only exists in injected
        """
        i = Injections("testinjection")
        assert not i.injected(self.temp_file_path), "Injected check returned true when not injected yet."
        i.inject(self.temp_file_path, self.test_injection)
        i.commit()
        assert i.in_noninjected_file(self.temp_file_path, self.permanent_string)
        assert not i.in_noninjected_file(self.temp_file_path, self.test_injection)

    def test_injected_injects_after_overrides(self):
        """
        re-injecting into a file will come after all other content
        """
        ORIGINAL_STRING = """
#testinjection
injectme
#testinjection

#OVERRIDE
overidden content
#OVERRIDE

non-override content
        """.strip()
        i = Injections("testinjection", override="OVERRIDE")
        c = i.inject_content(ORIGINAL_STRING, "injectme")
        assert c.find("injectme") > c.find("non-override content")

    def test_created(self):
        """ Test the injection creates a file if it does not exist """
        i = Injections("testinjection")
        new_file = os.path.join(self.temp_dir, "testcreated")
        i.inject(new_file, self.test_injection)
        i.commit()
        assert os.path.exists(new_file), "File was not generated on injection!"
