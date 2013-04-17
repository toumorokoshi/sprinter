"""
Installs a package from whatever the native package manager is
(apt-get for debian-based, brew for OS X)
[env]
formula = sprinter.formulas.package
debian = git
brew = git
"""
import os

from sprinter.formulastandard import FormulaStandard
from sprinter import lib


class PackageFormula(FormulaStandard):

    def __init__(self, environment):
        super(PackageFormula, self).__init__(environment)
        self.package_manager, self.manager_installed, self.sudo_required, self.args = self.__get_package_manager()

    def setup(self, feature_name, config):
        self.__install_package(feature_name, config)
        super(PackageFormula, self).setup(feature_name, config)

    def update(self, feature_name, config):
        if 'formula' not in config['source'] or \
                config['source']['formula'] != config['target']['formula']:
            self.__install_package(feature_name, config['target'])
        super(PackageFormula, self).update(feature_name, config)

    def __install_package(self, feature_name, config):
        if self.package_manager in config:
            if not self.manager_installed:
                if self.package_manager == "brew":
                    if not self.__install_brew():
                        self.logger.info("Unable to install package! skipping...")
                        return
            package = config[self.package_manager]
            self.logger.info("Installing %s..." % package)
            call_command = "%s %s install %s" % (self.package_manager, self.args, package)
            if self.sudo_required:
                call_command = "sudo " + call_command
            self.logger.debug("Calling command: %s" % call_command)
            lib.call(call_command)

    def __get_package_manager(self):
        """
        Installs and verifies package manager
        """
        package = ""
        args = ""
        sudo_required = True
        if self.system.isOSX():
            package = "brew"
            sudo_required = False
        elif self.system.isDebianBased():
            package = "apt-get"
            args = "-y"
        elif self.system.isFedoraBased():
            package = "yum"
        installed = lib.which(package) is not None
        if not installed:
            self.logger.error("package manager %s is not installed!" % package)
        return package, installed, sudo_required, args

    def __install_brew(self):
        """
        install brew if possible
        """
        if lib.which("brew") is None:
            if not os.path.exists('/usr/bin/xcodebuild'):
                self.logger.error("Unable to install brew! Please install xcode command line tools:")
                self.logger.error("https://developer.apple.com/xcode/")
                return False
            else:
                self.logger.info("Installing brew....")
                lib.call('ruby -e "$(curl -fsSL https://raw.github.com/mxcl/homebrew/go)"')
        return True
