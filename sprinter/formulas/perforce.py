"""
Creates a git repository and places it at the install location.

[perforce]
formula = sprinter.formulas.perforce
inputs = p4username
         p4password?
version = r10.1
root_path = ~/p4/
username = %(config:p4username)s
password = %(config:p4password)s
port = perforce.local:1666 client = %(config:node)s
"""
import os
import shutil
import re
import urllib

from sprinter.formulabase import FormulaBase

url_template = "http://filehost.perforce.com/perforce/%s/%s/p4"
exec_dict = {"r10.1": {"mac": "bin.macosx104u",
                       "linux": "bin.linux26x86_64"}}

p4settings_template = \
    """
P4USER=%(username)s
P4CLIENT=%(client)s
"""

p4client_template = \
    """
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


class PerforceFormula(FormulaBase):
    """ A sprinter formula for git"""

    def install(self, feature_name, config):
        super(PerforceFormula, self).install(feature_name, config)
        self.p4environ = dict(os.environ.items() + [('P4USER', config['username']),
                                                    ('P4PASSWD', config['password']),
                                                    ('P4CLIENT', config['client'])])
        self.__install_perforce(feature_name, config)
        if not os.path.exists(os.path.expanduser(config['root_path'])):
            os.makedirs(os.path.expanduser(config['root_path']))
        self.__write_p4settings(config)
        self.__configure_client(config)
        self.__sync_perforce(config)
        self.__add_p4_env(config)

    def update(self, feature_name, source_config, target_config):
        if source_config['version'] != target_config['version']:
            os.remove(os.path.join(self.directory.install_directory(feature_name), 'p4'))
            self.__install_perforce(self, feature_name, target_config)
        if target_config != source_config:
            self.__write_p4settings(target_config)
            self.__sync_perforce(target_config)
        self.__add_p4_env(target_config)

    def remove(self, feature_name, config):
        self.__destroy_perforce(config)

    def __install_perforce(self, feature_name, config):
        """ install perforce binary """
        exec_dir = exec_dict[config['version']]['mac'] if self.system.isOSX() else \
            exec_dict[config['version']]['linux']
        url = url_template % (config['version'], exec_dir)
        d = self.directory.install_directory(feature_name)
        if not os.path.exists(d):
            os.makedirs(d)
        self.logger.info("Downloading p4 executable...")
        urllib.urlretrieve(url, os.path.join(d, "p4"))
        self.directory.symlink_to_bin("p4", os.path.join(d, "p4"))
        self.p4_command = os.path.join(d, "p4")

    def __write_p4settings(self, config):
        """ write perforce settings """
        self.logger.info("Writing p4settings...")
        root_dir = os.path.expanduser(config['root_path'] % self.environment.target.get_context_dict())
        p4settings_path = os.path.join(root_dir, ".p4settings")
        out_content = p4settings_template % config
        if os.path.exists(p4settings_path) and out_content != open(p4settings_path, "r+").read():
            overwrite = self.lib.prompt("p4settings already exists at %s. Overwrite?" % root_dir,
                                        default="no",
                                        boolean=True)
            if overwrite:
                self.logger.info("Overwriting existing p4settings...")
                os.remove(p4settings_path)
            else:
                return
        with open(p4settings_path, "w+") as p4settings_file:
            p4settings_file.write(p4settings_template % config)
            add_p4passwd = self.lib.prompt("Also insert p4passwd? " +
                                           "(password will be stored in plaintext in a file in your perforce root)",
                                           default="no",
                                           boolean=True)
            if add_p4passwd:
                p4settings_file.write("\nP4PASSWD=%s" % config['password'])

    def __configure_client(self, config):
        """ write the perforce client """
        overwrite = self.lib.prompt("Would you like to overwrite the client workspace in perforce?",
                                    default="yes",
                                    boolean=True)
        if overwrite:
            self.logger.info("Configuring p4 client...")
            os.chdir(os.path.expanduser(config['root_path'] % self.environment.target.get_context_dict()))
            config['root_path'] = os.path.expanduser(config['root_path'])
            config['hostname'] = self.system.node
            config['p4view'] = config['p4view'] % self.environment.target.get_context_dict()
            client = re.sub('//depot', '    //depot', p4client_template % config)
            cwd = os.path.expanduser(config['root_path'] % self.environment.target.get_context_dict())
            self.logger.info(self.lib.call("%s client -i" % self.p4_command,
                                           stdin=client,
                                           env=self.p4environ,
                                           cwd=cwd))

    def __sync_perforce(self, config):
        """ prompt and sync perforce """
        sync = self.lib.prompt("would you like to sync your perforce root?",
                               default="yes",
                               boolean=True)
        if sync:
            self.logger.info("Syncing perforce root... (this can take a while).")
            cwd = os.path.expanduser(config['root_path'] % self.environment.target.get_context_dict())
            self.logger.info(self.lib.call("%s sync" % self.p4_command,
                                           env=self.p4environ,
                                           cwd=cwd))

    def __add_p4_env(self, config):
        self.directory.add_to_rc('export P4PORT=%s' % config['port'])
        self.directory.add_to_rc('export P4CONFIG=.p4settings')

    def __destroy_perforce(self, config):
        """ destroy the perforce root """
        sync = self.lib.prompt("would you like to completely remove the perforce root?", default="no")
        if sync.lower().startswith('y'):
            self.logger.info("Removing %s..." % config['root_path'])
            shutil.rmtree(os.path.expanduser(config['root_path'] % self.environment.get_context_dict()))
