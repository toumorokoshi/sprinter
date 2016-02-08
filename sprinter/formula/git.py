"""
Creates a git repository and places it at the install location.

[sub]
formula = sprinter.formula.git
url = https://github.com/toumorokoshi/sub.git
branch = toumorokoshi
rc = . %(sub:root_dir)s/libexec/sub-init
"""
from __future__ import unicode_literals
import logging
import os

from sprinter.formula.base import FormulaBase
import sprinter.lib as lib


class GitException(Exception):
    pass


class GitFormula(FormulaBase):
    """ A sprinter formula for git"""

    required_options = FormulaBase.required_options + ['url']
    valid_options = FormulaBase.valid_options + ['branch']

    def install(self):
        if not lib.which('git'):
            self.logger.warn("git is not installed! Please install git to install this feature.")
            return
        self.__clone_repo(self.target.get('url'),
                          self.directory.install_directory(self.feature_name),
                          branch=self.target.get('branch', 'master'))
        FormulaBase.install(self)

    def update(self):
        if not lib.which('git'):
            self.logger.warn("git is not installed! Please install git to install this feature.")
            return
        target_directory = self.directory.install_directory(self.feature_name)
        source_branch = self.source.get('branch', 'master')
        target_branch = self.target.get('branch', 'master')

        if not os.path.exists(target_directory):
            # directory doesn't exist, so we just clone again
            self.logger.debug("No repository cloned. Re-cloning...")
            self.__clone_repo(self.target.get('url'),
                              target_directory,
                              branch=target_branch)

        if self.target.get('url') != self.source.get('url'):

            self.logger.debug("Old git repository Found. Deleting...")
            self.directory.remove_feature(self.feature_name)
            self.__clone_repo(self.target.get('url'),
                              target_directory,
                              branch=self.target.get('branch', 'master'))

        elif source_branch != target_branch:
            self.__checkout_branch(target_directory, target_branch)

        else:
            if not os.path.exists(target_directory):
                self.logger.debug("No repository cloned. Re-cloning...")
                self.__clone_repo(self.target.get('url'),
                                  target_directory,
                                  branch=target_branch)
            self.__fetch_merge_repo(target_directory, target_branch)

        FormulaBase.update(self)
        return True

    def __git_branch(self, target_directory):
        # git -C $nemesis_src_root rev-parse --abbrev-ref HEAD
        error, output = lib.call("git -C {dir} rev-parse --abbrev-ref HEAD".format(
            dir=target_directory), output_log_level=logging.DEBUG)
        if error:
            self.logger.info(output)
            raise GitException("An error occurred while looking up the current git branch!")

    def __checkout_branch(self, target_directory, branch):
        git_opts = {
            'branch': branch,
            'dir': target_directory
        }
        self.logger.debug("Checking out branch {branch}...".format(**git_opts))
        for command in ("git -C {dir} fetch origin {branch}".format(**git_opts),
                        "git -C {dir} checkout {branch}".format(**git_opts)):
            error, output = lib.call(
                command,
                output_log_level=logging.DEBUG,
                cwd=target_directory
            )
            if error:
                self.logger.info(output)
                raise GitException("An error occurred when checking out a branch!")

    def __clone_repo(self, repo_url, target_directory, branch):
        git_opts = {
            'url': repo_url,
            'branch': branch,
            'dir': target_directory
        }
        self.logger.debug("Cloning repository {url} into {dir}...".format(**git_opts))
        error, output = lib.call("git clone {url} {dir}".format(**git_opts),
                                 output_log_level=logging.DEBUG)
        if error:
            self.logger.info(output)
            raise GitException("An error occurred when cloning!")
        self.__checkout_branch(target_directory, branch)

    def __fetch_merge_repo(self, target_directory, target_branch):
        git_opts = {
            'branch': target_branch,
            'dir': target_directory
        }
        self.logger.debug("Fetching branch {branch}...".format(**git_opts))
        # os.chdir(target_directory)

        error, output = lib.call("git -C {dir} fetch origin {branch}".format(**git_opts),
                                 output_log_level=logging.DEBUG)
        if error:
            self.logger.info(output)
            raise GitException("An error occurred while fetching!")

        self.logger.info(output)
        self.logger.debug("Merging branch {branch}...".format(**git_opts))
        error, output = lib.call("git -C {dir} merge --ff-only origin/{branch}".format(**git_opts),
                                 output_log_level=logging.DEBUG)
        if error:
            #do not want to raise exception on merge failures/conflicts
            self.logger.warning(output)
        else:
            self.logger.info(output)
