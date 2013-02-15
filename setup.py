#!/usr/bin/env python

from distutils.core import setup

setup(name='sprinter',
      version='1.0',
      description='a utility library to help environment bootstrapping scripts',
      author='Yusuke Tsutsumi',
      author_email='yusuke@yusuketsutsumi.com',
      packages=['sprinter', 'sprinter.recipes'],
      entry_points={
        'console_scripts': [
            'sprinter = sprinter.install:main'
        ]
      }
     )
