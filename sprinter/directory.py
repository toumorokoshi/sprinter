"""
directory.py stores methodology to install various files and
packages to different locations.

"""
import logging
import os
import shutil
import stat

rc_template = """
export PATH=%s:$PATH
"""


class DirectoryException(Exception):
    """ An exception to specify it's a directory """


class Directory(object):

    root_dir = None  # path to the root directory
    manifest_path = None  # path to the manifest file
    new = False  # determines if the directory is for a new environment or not
    rewrite_rc = True  # if set to false, the existing rc file will be
                       # preserved, and will not be modifiable
    rc_file = None  # file handler for rc file

    def __init__(self, namespace, rewrite_rc=True, sprinter_root=os.path.join("~", ".sprinter"),
                 logger=logging.getLogger('sprinter')):
        """ takes in a namespace directory to initialize, defaults to .sprinter otherwise."""
        self.root_dir = os.path.expanduser(os.path.join(sprinter_root, namespace))
        self.logger = logger
        self.new = not os.path.exists(self.root_dir)
        self.manifest_path = os.path.join(self.root_dir, "manifest.cfg")
        self.rewrite_rc = rewrite_rc

    def __del__(self):
        if self.rc_file:
            self.rc_file.close()

    def initialize(self):
        """ Generate the root directory root if it doesn't already exist """
        if not os.path.exists(self.root_dir):
            os.makedirs(self.root_dir)
        assert os.path.isdir(self.root_dir), "%s is not a directory! Please move or remove it." % self.root_dir
        for d in ["bin", "lib", "include"]:
            target_path = os.path.join(self.root_dir, d)
            if not os.path.exists(target_path):
                os.makedirs(target_path)
        if not os.path.exists(self.manifest_path):
            open(self.manifest_path, "w+").close()
        self.new = False

    def remove(self):
        """ Removes the sprinter directory, if it exists """
        if self.rc_file:
            self.rc_file.close()
        shutil.rmtree(self.root_dir)

    def symlink_to_bin(self, name, path):
        """ Symlink an object at path to name in the bin folder. """
        self.__symlink_dir("bin", name, path)
        os.chmod(os.path.join(self.root_dir, "bin", name), stat.S_IXUSR)
        os.chmod(os.path.join(self.root_dir, "bin", name), stat.S_IXUSR | stat.S_IRUSR)

    def remove_from_bin(self, name):
        """ Remove an object from the bin folder. """
        target_path = os.path.join(self.root_dir, "bin", name)
        if os.path.isdir(target_path):
            shutil.rmtree(target_path)
        else:
            os.unlink(target_path)

    def symlink_to_lib(self, name, path):
        """ Symlink an object at path to name in the lib folder. """
        self.__symlink_dir("lib", name, path)

    def symlink_to_include(self, name, path):
        """ Symlink an object at path to name in the lib folder. """
        self.__symlink_dir("include", name, path)

    def bin_path(self):
        """ return the bin directory path """
        return os.path.join(self.root_dir, "bin")

    def lib_path(self):
        """ return the lib directory path """
        return os.path.join(self.root_dir, "lib")

    def include_path(self):
        """ return the include directory path """
        return os.path.join(self.root_dir, "include")

    def install_directory(self, feature_name):
        """
        return a path to the install directory that the feature should install to.
        """
        return os.path.join(self.root_dir, "features", feature_name)

    def add_to_rc(self, content):
        """
        add content to the rc script.
        """
        if not self.rewrite_rc:
            raise DirectoryException("Error! Directory was not intialized w/ rewrite_rc.")
        if not self.rc_file:
            self.rc_path, self.rc_file = self.__get_rc_handle(self.root_dir)
        self.rc_file.write(content + '\n')

    def __get_rc_handle(self, root_dir):
        """ get the filepath and filehandle to the rc file for the environment """
        rc_path = os.path.join(root_dir, '.rc')
        if not os.path.exists(rc_path):
            fh = open(rc_path, "w+")
            fh.write(rc_template % os.path.join(root_dir, "bin"))
        return (rc_path, open(rc_path, "w+"))

    def __symlink_dir(self, dir_name, name, path):
        """
        Symlink an object at path to name in the dir_name folder. remove it if it already exists.
        """
        target_path = os.path.join(self.root_dir, dir_name, name)
        if os.path.exists(target_path):
            if os.path.islink(target_path):
                os.remove(target_path)
            else:
                self.logger.warn("%s is not a symlink! please remove it manually." % target_path)
                return
        os.symlink(path, target_path)
