"""
Injections.py handles injections into various configuration files
throughout files on the file system.

These operations are batched and applied together with the commit
command, or applied separately with the destructive_inject and
destructive_clear..
"""
from __future__ import unicode_literals
import codecs
import logging
import os
import re
import shutil
from ..compat import _unicode


class Injections(object):
    """
    Injections are staged until they are committed with the commit()
    method. This allow for aggregations until the commiting is ready
    to be performed.
    """

    logger = None  # logging object
    wrapper = None  # the string to wrap around the content.
    inject_dict = {}  # dictionary holding the injection object
    clear_set = set()  # list holding the filenames to clear injection from

    def __init__(self, wrapper, override=None, logger="sprinter"):
        wrapper = _unicode(wrapper)
        if override:
            self.override_match = re.compile(
                "(\n?#%s\n.*#%s\n)" % (override, override), re.DOTALL
            )
        else:
            self.override_match = None
        self.wrapper = "#%s" % wrapper
        self.wrapper_match = re.compile(
            "\n?#%s\n.*#%s\n" % (wrapper, wrapper), re.DOTALL
        )
        self.logger = logging.getLogger(logger)
        self.inject_dict = {}
        self.clear_set = set()

    def inject(self, filename, content):
        """add the injection content to the dictionary"""
        # ensure content always has one trailing newline
        content = _unicode(content).rstrip() + "\n"
        if filename not in self.inject_dict:
            self.inject_dict[filename] = ""
        self.inject_dict[filename] += content

    def clear(self, filename):
        """add the file to the list of files to clear"""
        self.clear_set.add(filename)

    def clear_all(self):
        """Clear all files that are currently prepped to be injected"""
        for filename in self.inject_dict:
            self.clear_set.add(filename)

    def commit(self):
        """commit the injections desired, overwriting any previous injections in the file."""
        self.logger.debug("Starting injections...")
        self.logger.debug("Injections dict is:")
        self.logger.debug(self.inject_dict)
        self.logger.debug("Clear list is:")
        self.logger.debug(self.clear_set)
        for filename, content in self.inject_dict.items():
            content = _unicode(content)
            self.logger.debug("Injecting values into %s..." % filename)
            self.destructive_inject(filename, content)
        for filename in self.clear_set:
            self.logger.debug("Clearing injection from %s..." % filename)
            self.destructive_clear(filename)

    def injected(self, filename):
        """Return true if the file has already been injected before."""
        full_path = os.path.expanduser(filename)
        if not os.path.exists(full_path):
            return False
        with codecs.open(full_path, "r+", encoding="utf-8") as fh:
            contents = fh.read()
        return self.wrapper_match.search(contents) is not None

    def destructive_inject(self, filename, content):
        """
        Injects the injections desired immediately. This should
        generally be run only during the commit phase, when no future
        injections will be done.
        """
        content = _unicode(content)
        backup_file(filename)
        full_path = self.__generate_file(filename)
        with codecs.open(full_path, "r", encoding="utf-8") as f:
            new_content = self.inject_content(f.read(), content)
        with codecs.open(full_path, "w+", encoding="utf-8") as f:
            f.write(new_content)

    def destructive_clear(self, filename):
        backup_file(filename)
        if not os.path.exists(os.path.expanduser(filename)):
            return
        full_path = self.__generate_file(filename)
        with codecs.open(full_path, "r", encoding="utf-8") as f:
            new_content = self.clear_content(f.read())
        with codecs.open(full_path, "w+", encoding="utf-8") as f:
            f.write(new_content)

    def __generate_file(self, file_path):
        """
        Generate the file at the file_path desired. Creates any needed
        directories on the way. returns the absolute path of the file.
        """
        file_path = os.path.expanduser(file_path)
        if not os.path.exists(os.path.dirname(file_path)):
            self.logger.debug(
                "Directories missing! Creating directories for %s..." % file_path
            )
            os.makedirs(os.path.dirname(file_path))
        if not os.path.exists(file_path):
            open(file_path, "w+").close()
        return file_path

    def in_noninjected_file(self, file_path, content):
        """Checks if a string exists in the file, sans the injected"""
        if os.path.exists(file_path):
            file_content = codecs.open(file_path, encoding="utf-8").read()
            file_content = self.wrapper_match.sub("", file_content)
        else:
            file_content = ""
        return file_content.find(content) != -1

    def inject_content(self, content, inject_string):
        """
        Inject inject_string into a text buffer, wrapped with
        #{{ wrapper }} comments if condition lambda is not
        satisfied or is None. Remove old instances of injects if they
        exist.
        """
        inject_string = _unicode(inject_string)
        content = self.wrapper_match.sub("", _unicode(content))
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
%s
""" % (
            self.wrapper,
            inject_string.rstrip(),
            self.wrapper,
        )
        if self.override_match:
            content += sprinter_overrides.rstrip() + "\n"
        return content

    def clear_content(self, content):
        """
        Clear the injected content from the content buffer, and return the results
        """
        content = _unicode(content)
        return self.wrapper_match.sub("", content)


def backup_file(filename):
    """create a backup of the file desired"""
    if not os.path.exists(filename):
        return

    BACKUP_SUFFIX = ".sprinter.bak"

    backup_filename = filename + BACKUP_SUFFIX
    shutil.copyfile(filename, backup_filename)
