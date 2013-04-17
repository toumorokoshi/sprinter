#!/usr/bin/env python

try:
    from setuptools import setup
except:
    from distutils.core import setup

setup(name='sprinter',
      version='0.4.0',
      description='a utility library to help environment bootstrapping scripts',
      author='Yusuke Tsutsumi',
      author_email='yusuke@yusuketsutsumi.com',
      url='http://toumorokoshi.github.io/sprinter',
      packages=['sprinter', 'sprinter.formulas'],
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
      },
      test_suite='tests'
      )
