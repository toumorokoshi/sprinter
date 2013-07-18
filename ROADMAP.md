Roadmap
-------

Refactor:

* unpack has a bug with not symlinking to the proper directory

TODO:
* Directory behavior changed to warn if a directory is not a symlink, not throw an error.
* test authenticated get catches unauthorized error
* test the 'bash' clause in command

This page highlights Sprinter's roadmap to reach 1.0
release. Currently sprinter is at version 0.6

### 0.7
* Migrate 'sprinter.formulas' to 'sprinter.formula'

# Before 1.0
The documentation needs to properly and completely document
the sprinter libraries and extension design:

* All formulas sufficiently tested
* ensure proper coverage for environment
* Add doc section for 'phases' and phases keyword in config
* Finish up formula functionality

### 1.0
Success! A Stable library that can be used to install environments to machines with ease

### Post 1.0
* Move all formulas out of the core sprinter repository
* Investigate integrating buildout recipe compatability?
