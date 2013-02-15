"""
Unpacks and deploys to a location
"""

import gzip
import os
import tarfile
import urllib
from StringIO import StringIO

from sprinter.recipebase import RecipeBase


class UnpackRecipe(RecipeBase):
    """ A sprinter recipe for unpacking a compressed package and extracting it"""

    def setup(self, directory, config):
        pass

    def update(self, config):
        pass

    def destroy(self, config):
        pass

    def __extract_targz(url, target_dir):
        """ extract a targz and install to the target directory """
        gz = gzip.GzipFile(fileobj=StringIO(urllib.urlopen(url).read()))
        tf = tarfile.TarFile(fileobj=gz)
        if not os.path.exists(target_dir):
            os.mkdir(target_dir)
        tf.extractall(path=target_dir)
