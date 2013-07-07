Manifests
=========

This covers the configuration required for a manifest, and the advanced aspects involved.

Special Sections
----------------

The following sections have a special meaning in a manifest:

config
######

The config section is where all user variables are stored. in
addition, it can also house the name of the environment, input
variables, and any standard confguration you need in your environment.

One can also add messages to the beginnig and the end of sprinter with the following variables:

* message_success: print a message at the end of a sprinter command, on success
* message_failure: print a message at the end of a sprinter command, on failure

Variable substitution
---------------------

Feature configurations in a manifest have the ability to reference
each other: specifically, they utilized the following format::

	%(FEATURE:PROPERTY)s

E.G. something like `%(git:configpath)s` will reference the
  'configpath' property of the 'git' feature. In addition to other
  features, it is also possible to reference the config sections as
  well, with:

	%(config:PROPERTY)

Common usage examples for this include having a single username
variable in the input, then resolving it into subsequent features
with: `%(config:username)s`

Filters
#######

Sprinter also supports some filters, to convert strings into a desired
format. For example, to escape special characters, you can use:

%(config:password|escaped)

To reference the password variable, escaped. The escaped function uses the 're.escape' method in python.


