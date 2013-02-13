"""
The install script for a sprinter-based setup script.
"""
import sys
import argparse

description = \
"""
Install an environment as specified in a sprinter config file
"""

parser = argparse.ArgumentParser(description=description)
parser.add_argument('target', metavar='T', nargs=1, help="The path to the manifest file to install")
parser.add_argument('--namespace', dest='namespace', help="Namespace to check environment against")


def main():
    args = parser.parse_args()
    pass

if __name__ == '__main__':
    if len(sys.argv) > 0 and sys.argv[1] == 'doctest':
        import doctest
        doctest.testmod()
    else:
        main()
