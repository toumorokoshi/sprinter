import tempfile
import shutil
from sprinter import environment
from sprinter.core.globals import create_default_config
import httpretty
from nose.plugins.attrib import attr
from mock import patch


@attr('full')
class TestLifecycle(object):
    """
    Test the sprinter lifecycle
    """

    def setup(self):
        self.global_config = create_default_config()
        self.global_config.set('shell', 'bash', 'false')
        self.global_config.set('shell', 'zsh', 'false')
        self.global_config.set('shell', 'gui', 'false')

    @httpretty.activate
    @patch('sprinter.lib.prompt')
    def test_full_lifecycle(self, prompt):
        """ Test the full sprinter lifecycle """
        prompt.return_value = "yes"
        temp_directory = tempfile.mkdtemp()
        try:
            TEST_URI = "http://testme.com/test.cfg"
            httpretty.register_uri(httpretty.GET, TEST_URI,
                                   body=open("./test_data/test_setup.cfg").read())
            env = environment.Environment(root=temp_directory, sprinter_namespace='test',
                                          global_config=self.global_config)
            env.target = TEST_URI
            env.install()
            env = environment.Environment(root=temp_directory, sprinter_namespace='test',
                                          global_config=self.global_config)
            env.source = TEST_URI
            env.remove()
        finally:
            shutil.rmtree(temp_directory)

    @httpretty.activate
    @patch('sprinter.lib.prompt')
    def test_standalone_sprinter(self, prompt):
        """ The standalone sprinter lifecycle should install, update, and remove sprinter """
        prompt.return_value = "yes"
        temp_directory = tempfile.mkdtemp()
        try:
            TEST_URI = "http://testme.com/test.cfg"
            httpretty.register_uri(httpretty.GET, TEST_URI,
                                   body=open("./examples/sprinter.cfg").read())
            # install
            env = environment.Environment(root=temp_directory, sprinter_namespace='test',
                                          global_config=self.global_config)
            env.target = TEST_URI
            env.install()
            # update
            env = environment.Environment(root=temp_directory, sprinter_namespace='test',
                                          global_config=self.global_config)
            env.target = TEST_URI
            env.source = TEST_URI
            env.update()
            # remove
            env = environment.Environment(root=temp_directory, sprinter_namespace='test',
                                          global_config=self.global_config)
            env.source = TEST_URI
            env.remove()
        finally:
            shutil.rmtree(temp_directory)
