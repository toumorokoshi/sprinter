#!/usr/bin/env python

try:
    from setuptools import setup
except:
    from distutils.core import setup

setup(name='sprinter',
      version='1.1.0',
      description='a utility library to help environment bootstrapping scripts',
      long_description=open('README.rst').read(),
      author='Yusuke Tsutsumi',
      author_email='yusuke@yusuketsutsumi.com',
      url='http://toumorokoshi.github.io/sprinter',
      packages=['sprinter', 'sprinter.formula'],
      install_requires=[
          'requests>=1.2.3',
          'pip>=1.3.1',
          'docopt>=0.6.1',
          'six>=1.4.1'
      ],
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Operating System :: MacOS',
          'Operating System :: POSIX :: Linux',
          'Topic :: System :: Software Distribution',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.3'
      ],
      entry_points={
          'console_scripts': [
              'sprinter = sprinter.install:main'
          ]
      },
      tests_require=['mock>=1.0.1', 'nose>=1.3.0', 'httpretty>=0.6.1'],
      test_suite='nose.collector'
)
