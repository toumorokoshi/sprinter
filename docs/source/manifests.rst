Manifests
=========

This covers the configuration required for a manifest, and the advanced aspects involved.

Special Sections
----------------

The following sections have a special meaning in a manifest:

config
######

The config section is where all user variables are stored. in addition, it can also house the name of the environment, and


Variable substitution
---------------------

Feature configurations in a manifest have the ability to reference each other: specifically, they utilized the following format::

	%(FEATURE:PROPERTY)s

E.G. something like `%(git:configpath)s` will reference the 'configpath' property of the 'git' feature. In addition to other features, it is also possible to reference the config sections as well, with:

	%(config:PROPERTY)

Common usage examples for this include having a single username variable in the input, then resolving it into subsequent features with: `%(config:username)s`
