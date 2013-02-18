#!/usr/bin/env python

try:
    from setuptools import setup
except:
    from distutils.core import setup

setup(name='sprinter',
      version='0.1',
      description='a utility library to help environment bootstrapping scripts',
      author='Yusuke Tsutsumi',
      author_email='yusuke@yusuketsutsumi.com',
      url='https://github.com/Toumorokoshi/sprinter',
      packages=['sprinter', 'sprinter.recipes'],
      classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: MacOS',
        'Operating System :: POSIX :: Linux',
        'Topic :: System :: Software Distribution',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
      ],
      entry_points={
        'console_scripts': [
            'sprinter = sprinter.install:main'
        ]
      }
     )
