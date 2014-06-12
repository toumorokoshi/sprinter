from __future__ import unicode_literals

import logging
import requests
import io
from clint.textui import progress

logger = logging.getLogger()


class BadCredentialsException(Exception):
    """ Returned if the credentials are incorrect """


class CertificateException(Exception):
    """ Returned if the certificates are incorrect """


def authenticated_get(username, password, url, verify=True):
    """
    Perform an authorized query to the url, and return the result
    """
    try:
        response = requests.get(url, auth=(username, password), verify=verify)
        if response.status_code == 401:
            raise BadCredentialsException(
                "Unable to authenticate user %s to %s with password provided!"
                % (username, url))
    except requests.exceptions.SSLError:
        raise CertificateException("Unable to verify certificate at %s!" % url)
    return response.content


def cleaned_request(request_type, *args, **kwargs):
    """ Perform a cleaned requests request """
    s = requests.Session()
    # this removes netrc checking
    s.trust_env = False
    return s.request(request_type, *args, **kwargs)


def download_to_bytesio(url):
    """ Return a bytesio object with a download bar """
    logger.info("Downloading url: {0}".format(url))
    r = cleaned_request('get', url, stream=True)
    stream = io.BytesIO()
    total_length = int(r.headers.get('content-length'))
    for chunk in progress.bar(r.iter_content(chunk_size=1024), expected_size=(total_length/1024) + 1):
        if chunk:
            stream.write(chunk)
    stream.seek(0)
    return stream
