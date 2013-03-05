Sprinter Recipes
================

Sprinter recipes are the building block of sprinter environments: they handle a specific piece of functionality of your environment, from cloning a git repository to install system packages.

In your sprinter environment configuration, each section (aside from some reserved names) represents a configured recipe. Here is an example:



.. code:: python

  [sub]
  recipe = sprinter.recipes.git
  url = git://github.com/Toumorokoshi/sub.git
  branch = yusuke
  rc = temp=`pwd`; cd %(sub:root_dir)s/libexec && . sub-init2 && cd $tmp

This section:

* utilizes the standard sprinter git recipe
* clones a git repo from the url specified
* checks out a specific branch yusuke
* adds the initialization command to the environment's .rc script 

Now let's talk more about recipes in detail.
