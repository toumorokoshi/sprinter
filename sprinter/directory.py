"""
directory.py stores methodology to install various files and
packages to different locations.

"""
import logging
import os
import shutil
import stat

# .rc always sources .env
rc_template = """[ -r "%s" ] && . %s
"""

# .env sources util.sh if necessary
env_template = """declare -f sprinter_prepend_path > /dev/null || . %s
"""

# utils.sh is the same for every namespace, only sourced once
utils_template="""
# don't add paths repeatedly to env vars
sprinter_prepend_path() {
    # $0 "/foo"         => "/foo:$PATH"
    # $0 "/foo" MANPATH => "/foo:$MANPATH"
    local dirp="$1"
    local path="${2:-PATH}"
    local list=$(eval echo '$'$path)
    if [ -d "$dirp" ] && [[ ":$list:" != *":$dirp:"* ]]; then
        # :+ syntax avoids dangling ":" in exported var
        export $path="${dirp}${list:+":$list"}"
    fi
}
"""

class DirectoryException(Exception):
    """ An exception to specify it's a directory """


class Directory(object):

    root_dir = None  # path to the root directory
    manifest_path = None  # path to the manifest file
    utils_path = None  # path to utils.sh file
    new = False  # determines if the directory is for a new environment or not
    rewrite_config = True  # if set to false, the existing rc and env files will be
                           # preserved, and will not be modifiable
    rc_file = None  # file handler for rc file
    env_file = None  # file handler for env file

    def __init__(self, namespace, rewrite_config=True, sprinter_root=os.path.join("~", ".sprinter"),
                 logger=logging.getLogger('sprinter')):
        """ takes in a namespace directory to initialize, defaults to .sprinter otherwise."""
        self.root_dir = os.path.expanduser(os.path.join(sprinter_root, namespace))
        self.logger = logger
        self.new = not os.path.exists(self.root_dir)
        self.manifest_path = os.path.join(self.root_dir, "manifest.cfg")
        self.utils_path = os.path.join(self.root_dir, "utils.sh")
        self.rewrite_config = rewrite_config

    def __del__(self):
        if self.rc_file:
            self.rc_file.close()
        if self.env_file:
            self.env_file.close()

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
        if not os.path.exists(self.utils_path):
            with open(self.utils_path, "w+") as fh:
                fh.write(utils_template)
        self.new = False

    def remove(self):
        """ Removes the sprinter directory, if it exists """
        if self.rc_file:
            self.rc_file.close()
        if self.env_file:
            self.env_file.close()
        shutil.rmtree(self.root_dir)

    def symlink_to_bin(self, name, path):
        """ Symlink an object at path to name in the bin folder. """
        self.__symlink_dir("bin", name, path)
        os.chmod(os.path.join(self.root_dir, "bin", name), os.stat(path).st_mode | stat.S_IXUSR | stat.S_IRUSR)

    def remove_from_bin(self, name):
        """ Remove an object from the bin folder. """
        self.__remove_path(os.path.join(self.root_dir, "bin", name))

    def remove_feature(self, feature_name):
        """ Remove an feature from the environment root folder. """
        if os.path.exists(self.install_directory(feature_name)):
            self.__remove_path(self.install_directory(feature_name))

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

    def add_to_env(self, content):
        """
        add content to the env script.
        """
        if not self.rewrite_config:
            raise DirectoryException("Error! Directory was not intialized w/ rewrite_config.")
        if not self.env_file:
            self.env_path, self.env_file = self.__get_env_handle(self.root_dir)
        self.env_file.write(content + '\n')

    def add_to_rc(self, content):
        """
        add content to the rc script.
        """
        if not self.rewrite_config:
            raise DirectoryException("Error! Directory was not intialized w/ rewrite_config.")
        if not self.rc_file:
            self.rc_path, self.rc_file = self.__get_rc_handle(self.root_dir)
        self.rc_file.write(content + '\n')

    def __remove_path(self, path):
        """ Remove an object """
        if not os.path.exists(path):
            self.logger.warn("Attempted to remove a non-existent path %s" % path)
            return
        try:
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.unlink(path)
        except OSError:
            self.logger.error("Unable to remove object at path %s" % path)
            raise DirectoryException("Unable to remove object at path %s" % path)

    def __get_env_handle(self, root_dir):
        """ get the filepath and filehandle to the .env file for the environment """
        env_path = os.path.join(root_dir, '.env')
        fh = open(env_path, "w+")
        # .env will source utils.sh if it hasn't already
        fh.write(env_template % self.utils_path)
        return (env_path, fh)

    def __get_rc_handle(self, root_dir):
        """ get the filepath and filehandle to the rc file for the environment """
        rc_path = os.path.join(root_dir, '.rc')
        env_path = os.path.join(root_dir, '.env')
        fh = open(rc_path, "w+")
        # .rc will always source .env
        fh.write(rc_template % (env_path, env_path))
        return (rc_path, fh)

    def __symlink_dir(self, dir_name, name, path):
        """
        Symlink an object at path to name in the dir_name folder. remove it if it already exists.
        """
        target_dir = os.path.join(self.root_dir, dir_name)
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        target_path = os.path.join(self.root_dir, dir_name, name)
        self.logger.debug("Attempting to symlink %s to %s..." % (path, target_path))
        if os.path.exists(target_path):
            if os.path.islink(target_path):
                os.remove(target_path)
            else:
                self.logger.warn("%s is not a symlink! please remove it manually." % target_path)
                return
        os.symlink(path, target_path)
