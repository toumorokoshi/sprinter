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

CURRENT_BRANCH = "git -C {dir} rev-parse --abbrev-ref HEAD"
CURRENT_REMOTE = "git -C {dir} remote get-url origin"
CLONE_REPO = "git clone {repo} {dir}"
CHECKOUT_BRANCH = "git -C {dir} checkout {branch}"
FETCH_BRANCH = "git -C {dir} fetch origin {branch}"
MERGE_BRANCH = "git -C {dir} merge --ff-only origin/{branch}"


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

        # if self.target.get('url') != self.source.get('url'):
        if self.__git(CURRENT_REMOTE, dir=target_directory)[1] != self.source.get('url'):

            self.logger.debug("Old git repository Found. Deleting...")
            self.directory.remove_feature(self.feature_name)
            self.__clone_repo(self.target.get('url'),
                              target_directory,
                              branch=self.target.get('branch', 'master'))

        # elif source_branch != target_branch:
        elif self.__git(CURRENT_BRANCH, dir=target_directory)[1] != target_branch:
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


    def __git(self, command, **kwargs):
        cmd = command.format(**kwargs)
        error, output = lib.call(cmd, output_log_level=logging.DEBUG)
        self.logger.info(output)
        if error:
            self.logger.warning(output)
        else:
            self.logger.info(output)

        return (error, output)

    def __checkout_branch(self, target_directory, branch):
        git_opts = {
            'branch': branch,
            'dir': target_directory
        }
        self.logger.debug("Checking out branch {branch}...".format(**git_opts))
        self.__git(FETCH_BRANCH, **git_opts)
        self.__git(CHECKOUT_BRANCH, **git_opts)

    def __clone_repo(self, repo_url, target_directory, branch):
        git_opts = {
            'repo': repo_url,
            'branch': branch,
            'dir': target_directory
        }
        self.logger.debug("Cloning repository {repo} into {dir}...".format(**git_opts))
        self.__git(CLONE_REPO, **git_opts)

    def __fetch_merge_repo(self, target_directory, target_branch):
        git_opts = {
            'branch': target_branch,
            'dir': target_directory
        }
        self.logger.debug("Fetching branch {branch}...".format(**git_opts))
        self.__git(FETCH_BRANCH, **git_opts)

        self.logger.debug("Merging branch {branch}...".format(**git_opts))
        error, output = self.__git(MERGE_BRANCH, **git_opts)

