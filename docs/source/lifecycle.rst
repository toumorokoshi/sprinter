Environment Lifecycle
=====================

The environment lifecycle was designed to be minimal and intuitive. Actions occur as they are necessary.

Installation
------------

When an environment is installed for the first time, the 'install'
directive is called on every feature.

Upgrade
-------

When an environment is upgraded:

* newly listed features have the 'install' directive called on them.
* existing features have the 'update' directive called on them.
* features no longer listed in have the 'remove' directive called on them.

Remove
------

When an environment is removed, every feature has the 'remove' directive called on them.

Deactivate
----------

When an environment is deactivated, every feature has the 'deactivate' directive called on them.

Activate
--------

When an environment is activated, every feature has the 'activate' directive called on them.
