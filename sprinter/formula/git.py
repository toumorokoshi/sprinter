"""
Clones a git repository and places it at the install location.
When configured with a path option, will reference an existing
git repo. Git repos outside the sprinter project folders will
not be deleted when the environment is removed. However, they
will be updated appropriately.

[my-project]
inputs = project_git_root==~/code/my_project#{ 'type': 'file' }
formula = sprinter.formula.git
url = https://github.com/me/my_project.git
git_root = %(config:project_git_root)s
branch = develop

[sub]
formula = sprinter.formula.git
url = https://github.com/toumorokoshi/sub.git
branch = master
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
UPDATE_ORIGIN = "git -C {dir} remote set-url origin {repo}"
UPDATE_OFFLINE_BRANCH = "git -C {dir} fetch origin {branch}:{branch}"

class GitException(Exception):
    pass


class GitFormula(FormulaBase):
    """ A sprinter formula for git"""

    required_options = FormulaBase.required_options + ['url']
    valid_options = FormulaBase.valid_options + ['branch', 'git_root']

    def install(self):
        if not lib.which('git'):
            self.logger.warn("git is not installed! Please install git to install this feature.")
            return
        install_dir = self.directory.install_directory(self.feature_name)
        git_root = self.target.get('git_root', None)
        target_path = git_root or install_dir
        target_branch = self.target.get('branch', 'master')
        git_opts = {
            'repo': self.target.get('url', None),
            'branch': target_branch,
            'dir': target_path
        }
        # no existing path is given or the path is not a git repo
        if (not target_path or not os.path.exists(target_path) or
                not self.__git(CURRENT_BRANCH, git_opts)[1]):
            self.__clone_repo(git_opts)

        # for an existing path, the git remote must match
        elif self.__git(CURRENT_REMOTE, git_opts)[1] != self.target.get('url'):
            raise GitException('Incorrect origin for local repo!')

        if self.__git(CURRENT_BRANCH, git_opts)[1] != target_branch:
            self.__checkout_branch(git_opts)

        FormulaBase.install(self)

    def update(self):
        if not lib.which('git'):
            self.logger.warn("git is not installed! Please install git to install this feature.")
            return
        install_dir = self.directory.install_directory(self.feature_name)
        git_root = self.target.get('git_root', None)
        target_path = git_root or install_dir
        source_branch = self.source.get('branch', 'master')
        target_branch = self.target.get('branch', 'master')
        git_opts = {
            'repo': self.target.get('url'),
            'branch': target_branch,
            'dir': target_path
        }

        # directory doesn't exist, or is not a git branch
        if (not target_path or not os.path.exists(target_path) or
                not self.__git(CURRENT_BRANCH, git_opts)[1]):
            self.logger.debug("No repository cloned. Re-cloning...")
            self.__clone_repo(git_opts)

        current_remote = self.__git(CURRENT_REMOTE, git_opts)[1]
        current_branch = self.__git(CURRENT_BRANCH, git_opts)[1]

        # for an existing path, the git remote must match
        if current_remote != self.target.get('url'):
            self.logger.debug("Updating origin url...")
            self.__git(UPDATE_ORIGIN, git_opts)

        if current_branch != target_branch:
            # update using "fetch origin [branch]:[branch]"
            self.__git(UPDATE_OFFLINE_BRANCH, git_opts)
        else:
            self.__fetch_merge_repo(git_opts)

        # change branches if the manifest has changed,
        # don't change branches if the user has changed branches
        if current_branch == source_branch and current_branch != target_branch:
            self.__checkout_branch(git_opts)

        FormulaBase.update(self)
        return True

    def __git(self, command, git_opts):
        cmd = command.format(**git_opts)
        error, output = lib.call(cmd, output_log_level=logging.DEBUG)
        self.logger.info(output)
        if error:
            self.logger.warning(output)
        else:
            self.logger.info(output)
        return (error, output.strip('\n \t'))

    def __checkout_branch(self, git_opts):
        self.logger.debug("Checking out branch {branch}...".format(**git_opts))
        self.__git(FETCH_BRANCH, git_opts)
        self.__git(CHECKOUT_BRANCH, git_opts)

    def __clone_repo(self, git_opts):
        self.logger.debug("Cloning repository {repo} into {dir}...".format(**git_opts))
        self.__git(CLONE_REPO, git_opts)

    def __fetch_merge_repo(self, git_opts):
        self.logger.debug("Fetching branch {branch}...".format(**git_opts))
        self.__git(FETCH_BRANCH, git_opts)

        self.logger.debug("Merging branch {branch}...".format(**git_opts))
        error, output = self.__git(MERGE_BRANCH, git_opts)
