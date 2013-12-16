"""
Utilities that extract files from packages
"""
import gzip
import io
import os
import shutil
import sys
import tarfile
import tempfile
import zipfile

import requests

from .command import call


class ExtractException(Exception):
    """ Returned if there was an issue with extracting a package """


def extract_targz(url, target_dir, remove_common_prefix=False, overwrite=False):
    """ extract a targz and install to the target directory """
    try:
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        gz = gzip.GzipFile(fileobj=io.BytesIO(requests.get(url).content))
        tf = tarfile.TarFile(fileobj=gz)
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        common_prefix = os.path.commonprefix(tf.getnames())
        if not common_prefix.endswith('/'):
            common_prefix += "/"
        for tfile in tf.getmembers():
            if remove_common_prefix:
                tfile.name = tfile.name.replace(common_prefix, "", 1)
            if tfile.name != "":
                target_path = os.path.join(tfile, target_dir)
                if target_path != target_dir and os.path.exists(target_path):
                    if overwrite:
                        remove_path(target_path)
                    else:
                        return
                tf.extract(tfile, target_dir)
    except OSError:
        e = sys.exc_info()[1]
        raise ExtractException(str(e))
    except IOError:
        e = sys.exc_info()[1]
        raise ExtractException(str(e))


def extract_zip(url, target_dir, remove_common_prefix=False, overwrite=False):
    try:
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        memory_file = io.BytesIO(requests.get(url).content)
        zip_file = zipfile.ZipFile(memory_file)
        common_prefix = os.path.commonprefix(zip_file.namelist())
        for zip_file_info in zip_file.infolist():
            target_path = zip_file_info.filename
            if remove_common_prefix:
                target_path = target_path.replace(common_prefix, "", 1)
            if target_path != "":
                target_path = os.path.join(target_dir, target_path)
                if target_path != target_dir and os.path.exists(target_path):
                    if overwrite:
                        remove_path(target_path)
                    else:
                        return
                zip_file.extract(zip_file_info, target_path)
    except OSError:
        raise ExtractException()
    except IOError:
        raise ExtractException()


def extract_dmg(url, target_dir, remove_common_prefix=False, overwrite=False):
    if remove_common_prefix:
        raise Exception("Remove common prefix for zip not implemented yet!")
    tmpdir = tempfile.mkdtemp()
    try:
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        temp_file = os.path.join(tmpdir, "temp.dmg")
        with open(temp_file, 'wb+') as fh:
            fh.write(cleaned_request('get', url).content)
        call("hdiutil attach %s -mountpoint /Volumes/a/" % temp_file)
        for f in os.listdir("/Volumes/a/"):
            if not f.startswith(".") and f != ' ':
                source_path = os.path.join("/Volumes/a", f)
                target_path = os.path.join(target_dir, f)
                if target_path != target_dir and os.path.exists(target_path):
                    if overwrite:
                        remove_path(target_path)
                    else:
                        return
                if os.path.isdir(source_path):
                    shutil.copytree(source_path, target_path)
                else:
                    shutil.copy(source_path, target_path)
    except OSError:
        raise ExtractException()
    except IOError:
        raise ExtractException()
    finally:
        call("hdiutil unmount /Volumes/a")
        shutil.rmtree(tmpdir)


def remove_path(target_path):
    """ Delete the target path """
    if os.path.isdir(target_path):
        shutil.rmtree(target_path)
    else:
        os.unlink(target_path)
