"""
Creates a perforce repository and places it at the install
location.

[perforce]
formula = sprinter.formula.perforce
inputs = p4username
         p4password?
version = r10.1
root_path = ~/p4/
username = %(config:p4username)s
password = %(config:p4password)s
port = perforce.local:1666
client = %(config:node)s
write_password_p4settings = true
overwrite_p4settings = false
overwrite_client = false
"""
import os
import re
import shutil
import requests
import sprinter.lib as lib
from sprinter.core import PHASE
from sprinter.formulabase import FormulaBase

P4V_APPLICATIONS = ['p4v.app', 'p4admin.app', 'p4merge.app']
url_prefix = "http://filehost.perforce.com/perforce/"
package_dict = {
    "r10.1": {
        "osx": {
            "p4": "r10.1/bin.macosx104u/p4",
            "p4v": "r10.1/bin.macosx104u/P4V.dmg"},
        "linux": {
            "p4": "r10.1/bin.linux26x86_64/p4",
            "p4v": "r10.1/bin.linux26x86_64/p4v.tgz"}
    },
    "r13.2": {
        "osx": {
            "p4": "r13.2/bin.macosx105x86_64/p4",
            "p4v": "r13.2/bin.macosx106x86_64/P4V.dmg"},
        "linux": {
            "p4": "r13.2/bin.linux26x86_64/p4",
            "p4v": "r13.2/bin.linux26x86_64/p4v.tgz"}
    }
}
                
    
class PerforceFormulaException(Exception):
    """Exceptions for perforce formula"""


class PerforceFormula(FormulaBase):

    valid_options = FormulaBase.valid_options + ['write_p4settings',
                                                 'write_password_p4settings',
                                                 'overwrite_p4settings',
                                                 'overwrite_client',
                                                 'client_default',
                                                 'client']

    required_options = FormulaBase.required_options + ['version', 'root_path', 'username',
                                                       'password', 'port', 'p4view']

    def prompt(self):
        if self.target:
            if not self.target.has('write_p4settings'):
                self.target.prompt('write_p4settings', 'Write a p4settings file?', default='yes')
                self.target.set_if_empty('write_p4settings', True)

            if self.environment.phase in (PHASE.INSTALL, PHASE.UPDATE):
                if self.target.is_affirmative('write_p4settings'):
                    p4settings_path = os.path.join(os.path.expanduser(self.target.get('root_path')),
                                                   '.p4settings')

                    if os.path.exists(p4settings_path):
                        self.target.prompt(
                            "overwrite_p4settings",
                            "p4settings already exists at %s. Overwrite?" % self.target.get('root_path'),
                            default="no", only_if_empty=True)

                    if (self.target.is_affirmative('write_p4settings') and
                        (not os.path.exists(p4settings_path)
                         or self.target.is_affirmative('overwrite_p4settings', default=False))):
                        self.target.prompt(
                            "write_password_p4settings",
                            "Insert the perforce password to your p4settings?\n" +
                            "(password will be stored in plaintext in a file in your perforce root)\n",
                            default="no", only_if_empty=True)
                self.target.prompt(
                    "client",
                    "Please choose your perforce client",
                    default=self.target.get('client_default', ''), only_if_empty=True)
            self.target.prompt(
                "overwrite_client",
                "Would you like to overwrite the client workspace in perforce?",
                default="yes", only_if_empty=True)

        elif self.environment.phase == PHASE.REMOVE:
                self.source.prompt(
                    "remove_p4root",
                    "Would you like to completely remove the p4 directory?",
                    default="no", only_if_empty=True)

    def install(self):
        config = self.target
        self.p4environ = dict(list(os.environ.items()) + [('P4USER', config.get('username')),
                                                          ('P4PASSWD', config.get('password')),
                                                          ('P4CLIENT', config.get('client'))])
        installed = self.__install_perforce(config)
        if not os.path.exists(os.path.expanduser(config.get('root_path'))):
            os.makedirs(os.path.expanduser(config['root_path']))
        if config.is_affirmative('write_p4settings'):
            self.__write_p4settings(config)
        if config.is_affirmative('overwrite_client') and installed:
            self.__configure_client(config)
        self.__add_p4_env(config)
        FormulaBase.install(self)

    def update(self):
        if self.source.get('version', 'r13.2') != self.target.get('version', 'r13.2'):
            os.unlink(os.path.join(self.directory.install_directory(self.feature_name), 'p4'))
            self.__install_perforce(self.target)
        self.__add_p4_env(self.target)
        FormulaBase.update(self)

    def remove(self):
        if self.source.is_affirmative('remove_p4root'):
            self.logger.info("Removing %s..." % self.source.get('root_path'))
            shutil.rmtree(os.path.expanduser(self.source.get('root_path')))
        FormulaBase.remove(self)

    def validate(self):
        FormulaBase.validate(self)
        config = self.target or self.source
        version = config.get('version', 'r13.2')
        if version not in package_dict:
            raise PerforceFormulaException("Version %s in not supported by perforce formula!\n" % version +
                                           "Supported versions are: %s" % ", ".join(package_dict.keys()))
        
    def __install_perforce(self, config):
        """ install perforce binary """
        if not self.system.is64bit():
            self.logger.warn("Perforce formula is only designed for 64 bit systems! Not install executables...")
            return False
        version = config.get('version', 'r13.2')
        key = 'osx' if self.system.isOSX() else 'linux'
        perforce_packages = package_dict[version][key]
        d = self.directory.install_directory(self.feature_name)
        if not os.path.exists(d):
            os.makedirs(d)
        self.logger.info("Downloading p4 executable...")
        with open(os.path.join(d, "p4"), 'wb+') as fh:
            fh.write(requests.get(url_prefix + perforce_packages['p4']).content)
        self.directory.symlink_to_bin("p4", os.path.join(d, "p4"))
        self.p4_command = os.path.join(d, "p4")
        self.logger.info("Installing p4v...")
        if self.system.isOSX():
            return self.__install_p4v_osx(url_prefix + perforce_packages['p4v'])
        else:
            return self.__install_p4v_linux(url_prefix + perforce_packages['p4v'])

    def __install_p4v_osx(self, url, overwrite=False):
        """ Install perforce applications and binaries for mac """
        package_exists = False
        root_dir = os.path.expanduser(os.path.join("~", "Applications"))
        package_exists = len([x for x in P4V_APPLICATIONS if os.path.exists(os.path.join(root_dir, x))])
        if not package_exists or overwrite:
            lib.extract_dmg(url, root_dir)
        else:
            self.logger.warn("P4V exists already in %s! Not overwriting..." % root_dir)
        return True

    def __install_p4v_linux(self, url):
        """ Install perforce applications and binaries for linux """
        lib.extract_targz(url,
                          self.directory.install_directory(self.feature_name),
                          remove_common_prefix=True)
        bin_path = os.path.join(self.directory.install_directory(self.feature_name), 'bin')
        for f in os.listdir(bin_path):
            self.directory.symlink_to_bin(f, os.path.join(bin_path, f))
        return True

    def __write_p4settings(self, config):
        """ write perforce settings """
        self.logger.info("Writing p4settings...")
        root_dir = os.path.expanduser(config.get('root_path'))
        p4settings_path = os.path.join(root_dir, ".p4settings")
        if os.path.exists(p4settings_path):
            if self.target.get('overwrite_p4settings', False):
                self.logger.info("Overwriting existing p4settings...")
                os.remove(p4settings_path)
            else:
                return
        with open(p4settings_path, "w+") as p4settings_file:
            p4settings_file.write(p4settings_template % config.to_dict())
            if config.get('write_password_p4settings', 'no'):
                p4settings_file.write("\nP4PASSWD=%s" % config['password'])

    def __add_p4_env(self, config):
        self.directory.add_to_env('export P4PORT=%s' % config['port'])
        if config.get('write_p4settings'):
            self.directory.add_to_env('export P4CONFIG=.p4settings')

    def __configure_client(self, config):
        """ write the perforce client """
        self.logger.info("Configuring p4 client...")
        client_dict = config.to_dict()
        client_dict['root_path'] = os.path.expanduser(config.get('root_path'))
        os.chdir(client_dict['root_path'])
        client_dict['hostname'] = self.system.node
        client_dict['p4view'] = config['p4view'] % self.environment.target.get_context_dict()
        client = re.sub('//depot', '    //depot', p4client_template % client_dict)
        self.logger.info(lib.call("%s client -i" % self.p4_command,
                                  stdin=client,
                                  env=self.p4environ,
                                  cwd=client_dict['root_path']))

p4settings_template = """
P4USER=%(username)s
P4CLIENT=%(client)s
"""

p4client_template = """
Client:	%(client)s

Update:	2012/12/03 00:16:24

Access:	2012/12/03 00:16:24

Owner:	%(username)s

Host:	%(hostname)s

Description:
        Created by %(username)s

Root:	%(root_path)s

Options:	noallwrite noclobber nocompress unlocked nomodtime normdir

LineEnd:	local

View:
%(p4view)s
"""
