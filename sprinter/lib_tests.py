"""
Tests for the library
"""

import os
import shutil
import tempfile
from base64 import b64encode

import httpretty
from nose import tools
from mock import patch

from sprinter.formulabase import FormulaBase
from sprinter.formula.env import EnvFormula
import sprinter.lib as lib
from sprinter.lib import (BadCredentialsException,
                          CommandMissingException)

TEST_TARGZ = "http://github.com/toumorokoshi/sprinter/tarball/master"


class TestLib(object):

        def test_get_formula_class(self):
            """ Test if a formula class is grabbed """
            class_object = lib.get_subclass_from_module("sprinter.formula.unpack",
                                                        FormulaBase)
            assert issubclass(class_object, FormulaBase)

        def test_get_formulabase(self):
            """ Test if formulabase can be grabbed"""
            class_object = lib.get_subclass_from_module("sprinter.formulabase",
                                                        FormulaBase)
            assert issubclass(class_object, FormulaBase)

        def skip_get_formula_class_correct_import(self):
            """ This test a bug with importing the proper class"""
            class_object = lib.get_subclass_from_module("sprinter.formula.env", FormulaBase)
            assert class_object == EnvFormula, \
                "%s class is not equal to %s" % (class_object, EnvFormula)

        def test_lib_errorcode(self):
            """ Test a proper error code is returned """
            assert lib.call("sh")[0] == 0, "cd call returns a non-zero exit!"
            assert lib.call("cd", shell=True)[0] == 0, "cd call returns a non-zero exit!"
            tools.eq_(lib.call("exit 1", shell=True)[0], 1, "exit 1 call returns a zero exit!")

        def test_lib_ampersandinquotes(self):
            """ An ampersand and other variables in quotes should not split """
            tools.eq_(lib.whitespace_smart_split('"ae09ge&eai"'), ['\"ae09ge&eai\"'])

        def test_lib_sprinterpip(self):
            """ Pip install command should work """
            tools.eq_(
                lib.whitespace_smart_split(
                    "pip install http://github.com/toumorokoshi/sprinter/tarball/master"),
                ['pip', 'install', 'http://github.com/toumorokoshi/sprinter/tarball/master'])

        def test_call_error(self):
            """ Test an exception is thrown for a non-existent command """
            try:
                lib.call("eahxanea0e0")
            except CommandMissingException:
                return
            raise("Bogus command without proper shell doesn't return proper exception!")

        def integrate_dmg(self):
            """ Test if the dmg install works """
            test_dir = tempfile.mkdtemp()
            try:
                lib.extract_dmg("https://dl.google.com/chrome/mac/stable/GGRM/googlechrome.dmg", test_dir)
                assert os.path.exists(os.path.join(test_dir, "Google Chrome.app")), "app was not extracted!"
            finally:
                shutil.rmtree(test_dir)

        def integrate_dmg_with_overwrite(self):
            """ Test if the dmg install works, with an overwrite """
            test_dir = tempfile.mkdtemp()
            try:
                os.mkdir(os.path.join(test_dir, "sprinter"))
                lib.extract_targz(TEST_TARGZ, test_dir, remove_common_prefix=True)
                assert not os.path.exists(os.path.join(test_dir, "sprinter", "sprinter"))
                lib.extract_targz(TEST_TARGZ, test_dir, remove_common_prefix=True, overwrite=True)
                assert os.path.exists(os.path.join(test_dir, "sprinter", "formulas"))
                lib.extract_dmg("https://dl.google.com/chrome/mac/stable/GGRM/googlechrome.dmg", test_dir, overwrite=True)
                assert os.path.exists(os.path.join(test_dir, "Google Chrome.app")), "app was not extracted!"
            finally:
                shutil.rmtree(test_dir)

        @httpretty.activate
        def test_targz(self):
            """ Test if the targz extract works """
            TEST_URI = "http://testme.com/test.tar.gz"
            httpretty.register_uri(httpretty.GET, TEST_URI,
                                   body=open("./test_data/test_tar.tar.gz", 'rb').read())
            test_dir = tempfile.mkdtemp()
            try:
                lib.extract_targz(TEST_URI, test_dir, remove_common_prefix=True)
                assert os.path.exists(os.path.join(test_dir, "sprinter"))
                assert os.path.isdir(os.path.join(test_dir, "sprinter"))
            finally:
                shutil.rmtree(test_dir)

        @httpretty.activate
        def test_targz_with_overwrite(self):
            """ Test if the targz extract works, and overwrites """
            TEST_URI = "http://testme.com/test.tar.gz"
            httpretty.register_uri(httpretty.GET, TEST_URI,
                                   body=open("./test_data/test_tar.tar.gz", 'rb').read())
            test_dir = tempfile.mkdtemp()
            try:
                os.mkdir(os.path.join(test_dir, "sprinter"))
                lib.extract_targz(TEST_URI, test_dir, remove_common_prefix=True)
                assert not os.path.exists(os.path.join(test_dir, "sprinter", "sprinter"))
                lib.extract_targz(TEST_URI, test_dir, remove_common_prefix=True, overwrite=True)
                assert os.path.exists(os.path.join(test_dir, "sprinter", "formulas"))
            finally:
                shutil.rmtree(test_dir)
               
        @httpretty.activate
        def test_zip(self):
            """ Test if the zip extract works """
            TEST_URI = "http://testme.com/test.zip"
            httpretty.register_uri(httpretty.GET, TEST_URI,
                                   body=open("./test_data/test_zip.zip", 'rb').read())
            test_dir = tempfile.mkdtemp()
            try:
                lib.extract_zip(TEST_URI, test_dir, remove_common_prefix=True)
                assert os.path.exists(os.path.join(test_dir, "sprinter"))
                assert os.path.isdir(os.path.join(test_dir, "sprinter"))
            finally:
                shutil.rmtree(test_dir)

        @httpretty.activate
        def test_zip_with_overwrite(self):
            """ Test if the zip extract works, and overwrites """
            TEST_URI = "http://testme.com/test.zip"
            httpretty.register_uri(httpretty.GET, TEST_URI,
                                   body=open("./test_data/test_zip.zip", 'rb').read())
            test_dir = tempfile.mkdtemp()
            try:
                os.mkdir(os.path.join(test_dir, "sprinter"))
                lib.extract_zip(TEST_URI, test_dir, remove_common_prefix=True)
                assert not os.path.exists(os.path.join(test_dir, "sprinter", "sprinter"))
                lib.extract_zip(TEST_URI, test_dir, remove_common_prefix=True, overwrite=True)
                assert os.path.exists(os.path.join(test_dir, "sprinter", "formulas"))
            finally:
                shutil.rmtree(test_dir)

        def test_remove_path(self):
            """ Remove path should handle removing a directory and a path """
            test_dir = tempfile.mkdtemp()
            try:
                # test directory
                test_target_dir = tempfile.mkdtemp(prefix=test_dir)
                lib.remove_path(test_target_dir)
                assert not os.path.exists(test_target_dir)
                
                # test file
                _, test_target_path = tempfile.mkstemp(prefix=test_dir)
                lib.remove_path(test_target_path)
                assert not os.path.exists(test_target_path)
            finally:
                shutil.rmtree(test_dir)

        def test_is_affirmative(self):
            """ the is_affirmative command should return true if a value is truthy """
            assert lib.is_affirmative("yes")
            assert lib.is_affirmative("t")
            assert lib.is_affirmative("y")
            assert lib.is_affirmative("True")
            assert not lib.is_affirmative("False")
            assert not lib.is_affirmative("gibberish")
            assert not lib.is_affirmative("coto")
            assert not lib.is_affirmative("eslaf")

        @httpretty.activate
        def test_authenticated_get(self):
            """ The authenticated get should pass in authentication headers """
            TEST_URI = "http://testme.com/test.html"
            CONTENT = "hello world"
            httpretty.register_uri(httpretty.GET, TEST_URI,
                                   body=CONTENT)
            returned_content = lib.authenticated_get("username", "password", TEST_URI)
            tools.eq_(returned_content.decode("utf-8"), CONTENT)
            tools.ok_("Authorization" in httpretty.last_request().headers)
            tools.eq_(httpretty.last_request().headers["Authorization"],
                      "Basic %s" % b64encode(('%s:%s' % ("username", "password")).encode("latin1")).strip().decode("utf-8"))

        @httpretty.activate
        @tools.raises(BadCredentialsException)
        def test_authenticated_failed_get(self):
            """ The authenticated failed get should throw a BadCredentials exception """
            TEST_URI = "http://testme.com/test.html"
            CONTENT = "hello world"
            httpretty.register_uri(httpretty.GET, TEST_URI,
                                   body=CONTENT, status=401)
            lib.authenticated_get("username", "password", TEST_URI)

        @patch.object(lib, 'call')
        def test_insert_environment_osx(self, call):
            """ Insert environment gui should inject variables into the environment """
            # TODO: write this test after functionality exists
