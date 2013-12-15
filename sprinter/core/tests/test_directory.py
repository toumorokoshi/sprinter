"""
Tests for directory class
"""
from __future__ import unicode_literals
import os
import shutil
import tempfile

from nose import tools
from mock import Mock, patch
from sprinter.directory import Directory, DirectoryException


class TestDirectory(object):
    """
    Test the directory object
    """

    def setup(self):
        self.temp_dir = tempfile.mkdtemp()
        self.directory = Directory('test', rewrite_config=True,
                                   sprinter_root=self.temp_dir)
        self.directory.initialize()

    def teardown(self):
        if hasattr(self, 'directory'):
            del(self.directory)
        shutil.rmtree(self.temp_dir)

    def test_initialize(self):
        """ The initialize method should generate the proper directories """
        self.directory.initialize()
        assert not self.directory.new,\
            "new variable should be set to false for existing directory!"
        assert os.path.exists(self.directory.bin_path()),\
            "bin directory should exist after initialize!"
        assert os.path.exists(self.directory.lib_path()),\
            "lib directory should exist after initialize!"

    def test_initialize_new(self):
        """ The initialize method should return new for a non-existent directory """
        new_temp_dir = self.temp_dir + "e09dia0d"
        directory = Directory('test', rewrite_config=False, sprinter_root=new_temp_dir)
        assert directory.new
        try:
            directory.initialize()
            assert not directory.new, "directory should not be new after initialization"
        finally:
            if os.path.exists(new_temp_dir):
                shutil.rmtree(new_temp_dir)

    def test_clear_feature_symlinks(self):
        """ clear feature symlinks """
        test_feature = 'woops'
        os.makedirs(self.directory.install_directory(test_feature))
        test_file = os.path.join(self.directory.install_directory(test_feature), 'test_file')
        with open(test_file, 'w+') as temp_file:
            temp_file.write('hobo')
        self.directory.symlink_to_bin('test_file', test_file)
        self.directory.symlink_to_lib('test_file', test_file)
        self.directory.clear_feature_symlinks(test_feature)
        assert not os.path.exists(os.path.join(self.directory.bin_path(), 'test_file'))
        assert not os.path.exists(os.path.join(self.directory.lib_path(), 'test_file'))

    def test_symlink_to_bin(self):
        """ symlink to bin should symlink to the bin sprinter environment folder """
        _, temp_file_path = tempfile.mkstemp()
        try:
            with open(temp_file_path, 'w+') as temp_file:
                temp_file.write('hobo')
            self.directory.symlink_to_bin('newfile', temp_file_path)
            assert os.path.islink(os.path.join(self.directory.bin_path(), 'newfile'))
            tools.eq_(open(os.path.join(self.directory.bin_path(), 'newfile')).read(),
                      open(temp_file_path).read(),
                      "File contents are different for symlinked files!")
            assert os.access(os.path.join(self.directory.bin_path(), 'newfile'), os.X_OK),\
                "File is not executable!"
        finally:
            os.unlink(temp_file_path)

    def test_symlink_to_bin_file_exists(self):
        """
        symlink to bin should not symlink to the bin sprinter environment
        folder if the file already exists.
        """
        _, temp_file_path = tempfile.mkstemp()
        bin_path = None
        try:
            with open(temp_file_path, 'w+') as temp_file:
                temp_file.write('hobo')
            bin_path = os.path.join(self.directory.bin_path(), 'newfile')
            with open(bin_path, 'w+') as temp_file:
                temp_file.write('hobomobo')
            self.directory.symlink_to_bin('newfile', temp_file_path)
            assert not os.path.islink(os.path.join(self.directory.bin_path(), 'newfile'))
        finally:
            os.unlink(temp_file_path)
            if bin_path and os.path.exists(bin_path):
                os.unlink(bin_path)

    def test_remove_from_bin_file_exists(self):
        """ removing from bin should remove a file from bin """
        _, temp_file_path = tempfile.mkstemp()
        try:
            with open(temp_file_path, 'w+') as temp_file:
                temp_file.write('hobo')
            self.directory.symlink_to_bin('newfile', temp_file_path)
            self.directory.remove_from_bin('newfile')
            assert not os.path.exists(os.path.join(self.directory.bin_path(), 'newfile'))
            os.mkdir(os.path.join(self.directory.bin_path(), 'newfolder'))
            self.directory.remove_from_bin('newfolder')
            assert not os.path.exists(os.path.join(self.directory.bin_path(), 'newfolder'))
        finally:
            os.unlink(temp_file_path)
            
    def test_remove_from_bin_no_file_warns(self):
        """ If a file doesn't exist and is attempted to be removed, a warning should fire """
        self.directory.logger.warn = Mock()
        self.directory.remove_from_bin('newfolder')
        assert self.directory.logger.warn.called

    @tools.raises(DirectoryException)
    def test_remove_feature_with_error_throws_exception(self):
        """ Attempting to remove a feature that throws an exception should raise a directory exception """
        with patch('shutil.rmtree') as mock:
            mock.side_effect = OSError()
            os.makedirs(self.directory.install_directory('test'))
            self.directory.remove_feature('test')

    def test_symlink_to_lib(self):
        """ symlink to lib should symlink to the lib sprinter environment folder """
        _, temp_file = tempfile.mkstemp()
        with open(temp_file, 'w+') as tfh:
            tfh.write('hobo')
        self.directory.symlink_to_lib('newfile', temp_file)
        assert os.path.islink(os.path.join(self.directory.lib_path(), 'newfile'))
        tools.eq_(open(os.path.join(self.directory.lib_path(), 'newfile')).read(),
                  open(temp_file).read(),
                  "File contents are different for symlinked files!")

    def test_symlink_to_lib_conflicts_with_existing_file(self):
        """ If the target file exists and is not a symlink, do not remove it """
        """ symlink to lib should symlink to the lib sprinter environment folder """
        _, temp_file = tempfile.mkstemp()
        with open(temp_file, 'w+') as tfh:
            tfh.write('hobo')
        os.makedirs(os.path.join(self.directory.lib_path(), 'newfile'))
        self.directory.symlink_to_lib('newfile', temp_file)
        assert not os.path.islink(os.path.join(self.directory.lib_path(), 'newfile'))

    def test_symlink_to_include(self):
        """ symlink to lib should symlink to the lib sprinter environment folder """
        _, temp_file = tempfile.mkstemp()
        with open(temp_file, 'w+') as tfh:
            tfh.write('hobo')
        self.directory.symlink_to_include('newfile', temp_file)
        assert os.path.islink(os.path.join(self.directory.include_path(), 'newfile'))
        tools.eq_(open(os.path.join(self.directory.include_path(), 'newfile')).read(),
                  open(temp_file).read(),
                  "File contents are different for symlinked files!")
        
    def test_add_to_rc(self):
        """ Test if the add_to_rc method adds to the rc """
        test_content = "THIS IS AN OOOGA BOOGA TEST "
        self.directory.add_to_rc(test_content)
        rc_file_path = os.path.join(self.directory.root_dir, ".rc")
        del(self.directory)
        assert open(rc_file_path).read().find(test_content) != -1,\
            "test content was not found!"
        
    @tools.raises(DirectoryException)
    def test_add_to_rc_norc_rewrite(self):
        """
        With the rc_rewrite flag false, an exception should be thrown if
        one attempts to write to it
        """
        directory = Directory('test', rewrite_config=False,
                              sprinter_root=self.temp_dir)
        directory.add_to_rc("test")

    def test_remove(self):
        """ Remove should remove the environment directory """
        self.directory.remove()
        assert not os.path.exists(self.directory.root_dir), "Path still exists after remove!"
