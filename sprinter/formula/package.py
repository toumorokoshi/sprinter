"""
Installs a package from whatever the native package manager is
(apt-get for debian-based, brew for OS X)
[git]
formula = sprinter.formula.package
apt-get = git
brew = git
"""
from sprinter.formulabase import FormulaBase
import sprinter.lib as lib
import logging


class PackageFormulaException(Exception):
    """ Errors with the package formula """


class PackageFormula(FormulaBase):

    valid_options = FormulaBase.valid_options + ['apt-get', 'brew', 'yum']

    def install(self):
        self.__get_package_manager()
        self.__install_package(self.target)
        FormulaBase.install(self)

    def update(self):
        self.__get_package_manager()
        install_package = False
        if self.package_manager and self.target.has(self.package_manager):
            if not self.source.has(self.package_manager):
                install_package = True
            if self.source.get(self.package_manager) != self.target.get(self.package_manager):
                install_package = True
        if install_package:
            self.__install_package(self.target)
        FormulaBase.update(self)

    def __install_package(self, config):
        if self.package_manager and config.has(self.package_manager):
            package = config.get(self.package_manager)
            self.logger.info("Installing %s..." % package)
            call_command = "%s%s install %s" % (self.package_manager, self.args, package)
            if self.sudo_required:
                call_command = "sudo " + call_command
            self.logger.debug("Calling command: %s" % call_command)
            # it's not possible to retain remember sudo privileges across shells unless they pipe
            # to STDOUT. Nothing we can do about that for now.
            lib.call(call_command, output_log_level=logging.DEBUG, stdout=None)

    def __get_package_manager(self):
        """
        Installs and verifies package manager
        """
        package_manager = ""
        args = ""
        sudo_required = True
        if self.system.isOSX():
            package_manager = "brew"
            sudo_required = False
        elif self.system.isDebianBased():
            package_manager = "apt-get"
            args = " -y"
        elif self.system.isFedoraBased():
            package_manager = "yum"
        if lib.which(package_manager) is None:
            self.logger.warn("Package manager %s not installed! Packages will not be installed."
                             % package_manager)
            self.package_manager = None
        self.package_manager = package_manager
        self.sudo_required = sudo_required
        self.args = args
