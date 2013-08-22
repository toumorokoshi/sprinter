Sprinter Formulas
=================

Sprinter formulas are the building block of sprinter environments:
they handle a specific piece of functionality of your environment,
from cloning a git repository to install system packages.

In your sprinter environment configuration, each section (aside from
config, which is intended for environment configuration) represents a
configured formula, knows as a :term:`feature <feature>`. Here is an
example:

.. code:: python

  [sub]
  formula = sprinter.formula.git
  url = git://github.com/Toumorokoshi/sub.git
  branch = yusuke
  rc = temp=`pwd`; cd %(sub:root_dir)s/libexec && . sub-init2 && cd $tmp

This section:

* utilizes the standard sprinter git formula
* clones a git repo from the url specified
* checks out a specific branch yusuke
* adds the initialization command to the environment's .rc script 

Configuration parameters vary from formula to formula, so look at the
documentation to figure out which parameters are available to you.

Now let's talk more about formulas in detail.

Where to find formulas
----------------------
Formulas are either included in the sprinter standard library, or can be sourced through python's pypi package repository, or through a url. 

A list of available formulas can be found on the :doc:`formulalist` page.

Standard Formula Options
------------------------

Although sprinter formulas perform different functions, they all have
a common set of functionality to facilitate workflows like adding
files to the init script.

These functions are:

* 'rc': this will add lines into the .rc of your environment, thereby
  being added to your environment if it's activated. (for setup and
  updates)
* 'env': this will add lines into the .env of your environment, thereby
  being added to your environment if it's activated. (for setup and
  updates)
* 'command': this will run the specified command after the formula is finished (for setup and updates)
* 'systems': this specifies the systems that this particular formula should run on. The currently supported values are:

  * osx = OSX systems
  * debian = debian-based systems
