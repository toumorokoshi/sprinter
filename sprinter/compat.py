"""
A set of abstractions to allow compatiblity between python 2 and 3
"""


def raise_exception(exc_type, exc_value, exc_traceback):
    """
    python 2-3 exception
    
    THIS DOES NOT WORK FOR SYNTAX EXCEPTIONS
    """
    # 3
    try:
        raise exc_type(exc_value).with_traceback(exc_traceback)
    # 2
    except SyntaxError:
        pass
        #raise exc_type, exc_value, exc_traceback

try:
    import configparser
except ImportError:
    import ConfigParser
    configparser = ConfigParser
