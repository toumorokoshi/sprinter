"""
Injections.py handles injections into various configuration files
throughout files on the file system.

These operations are batched and applied together with the commit
command, or applied separately with the destructive_inject and
destructive_clear..
"""

import logging
import os
import re


class Injections(object):
    """
    Injections are staged until they are committed with the commit()
    method. This allow for aggregations until the commiting is ready
    to be performed.
    """

    logger = None  # logging object
    wrapper = None  # the string to wrap around the content.
    inject_dict = {}  # dictionary holding the injection object
    clear_dict = set()  # list holding the filenames to clear injection from

    def __init__(self, wrapper, override=None, logger='sprinter'):
        if override:
            self.override_match = re.compile("(\n?#%s.*#%s)" % (override, override), re.DOTALL)
        else:
            self.override_match = None
        self.wrapper = "#%s" % wrapper
        self.wrapper_match = re.compile("\n?#%s.*#%s" % (wrapper, wrapper), re.DOTALL)
        self.logger = logging.getLogger(logger)

    def inject(self, filename, content):
        """ add the injection content to the dictionary """
        if filename in self.inject_dict:
            self.inject_dict[filename] += ("\n" + content)
        else:
            self.inject_dict[filename] = content

    def clear(self, filename):
        """ add the file to the list of files to clear """
        self.clear_dict.add(filename)

    def commit(self):
        """ commit the injections desired, overwriting any previous injections in the file. """
        self.logger.debug("Starting injections...")
        for filename, content in self.inject_dict.items():
            self.logger.info("Injecting values into %s..." % filename)
            self.destructive_inject(filename, content)
        for filename in self.clear_dict:
            self.logger.info("Clearing injection from %s..." % filename)
            self.__generate_file(filename)
            self.destructive_clear(filename)

    def injected(self, filename):
        """ Return true if the file has already been injected before. """
        full_path = os.path.expanduser(filename)
        if not os.path.exists(full_path):
            return False
        with open(full_path, 'r+') as fh:
            contents = fh.read()
        return self.wrapper_match.search(contents) is not None


    def destructive_inject(self, filename, content):
        """
        Injects the injections desired immediately. This should
        generally be run only during the commit phase, when no future
        injections will be done.
        """
        full_path = self.__generate_file(filename)
        with open(full_path, 'r') as f:
            new_content = self.inject_content(f.read(), content)
        with open(full_path, 'w+') as f:
            f.write(new_content)

    def destructive_clear(self, filename):
        full_path = self.__generate_file(filename)
        with open(full_path, 'r') as f:
            new_content = self.clear_content(f.read())
        with open(full_path, 'w+') as f:
            f.write(new_content)

    def __generate_file(self, file_path):
        """
        Generate the file at the file_path desired. Creates any needed
        directories on the way. returns the absolute path of the file.
        """
        file_path = os.path.expanduser(file_path)
        if not os.path.exists(os.path.dirname(file_path)):
            self.logger.debug("Directories missing! Creating directories for %s..." % file_path)
            os.makedirs(os.path.dirname(file_path))
        if not os.path.exists(file_path):
            open(file_path, "w+").close()
        return file_path

    def inject_content(self, content, inject_string):
        """
        Inject inject_string into a text buffer, wrapped with
        #{{ wrapper }} comments if condition lambda is not
        satisfied or is None. Remove old instances of injects if they
        exist.
        """
        content = self.wrapper_match.sub("", content)
        if self.override_match:
            sprinter_overrides = self.override_match.search(content)
            if sprinter_overrides:
                content = self.override_match.sub("", content)
                sprinter_overrides = sprinter_overrides.groups()[0]
            else:
                sprinter_overrides = ""
        content += """
%s
%s
%s""" % (self.wrapper, inject_string, self.wrapper)
        if self.override_match:
            content += "\n" + sprinter_overrides
        return content

    def clear_content(self, content):
        """
        Clear the injected content from the content buffer, and return the results
        """
        return self.wrapper_match.sub("", content)
