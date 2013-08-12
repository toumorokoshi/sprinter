Sprinter Formulas
=================

Sprinter formulas are the building block of sprinter environments:
they handle a specific piece of functionality of your environment,
from cloning a git repository to install system packages.

In your sprinter environment configuration, each section (aside from
some reserved names) represents a configured formula, knows as a
:term:`feature <feature>`. Here is an example:



.. code:: python

  [sub]
  recipe = sprinter.formulas.git
  url = git://github.com/Toumorokoshi/sub.git
  branch = yusuke
  rc = temp=`pwd`; cd %(sub:root_dir)s/libexec && . sub-init2 && cd $tmp

This section:

* utilizes the standard sprinter git recipe
* clones a git repo from the url specified
* checks out a specific branch yusuke
* adds the initialization command to the environment's .rc script 

Configuration parameters vary from recipe to recipe, so look at the
documentation to figure out which parameters are available to you.

Now let's talk more about formulas in detail.

Where to find formulas
----------------------
Currently, formulas can be found in one place:

1. contained inside the standard sprinter library. Currently the formulas include:

    * command, to execute a commnd
    * env, to add environment variables
    * git, for git repo cloning
    * package, to install packages from the package manager of your environment
    * perforce, to configure and install perforce
    * ssh, to set up an ssh key
    * template, to specialize a template and write it to a specified location
    * unpack, to unpack tar.gz files

Standard Formula Options
------------------------

Although sprinter formulas perform different functions, they all have
a common set of functionality to facilitate workflows like adding
files to the init script.

These functions are:

* 'rc': this will add lines into the .rc of your environment, thereby
  being added to your environment if it's activated. (for setup and
  updates)
* 'command': this will run the specified command after the recipe is finished (for setup and updates)
* 'systems': this specifies the systems that this particular recipe should run on. The currently supported values are:

  * osx = OSX systems
  * debian = debian-based systems
