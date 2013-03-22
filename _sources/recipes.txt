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

Configuration parameters vary from recipe to recipe, so look at the documentation to figure out which parameters are available to you.

Now let's talk more about recipes in detail.

Where to find recipes
---------------------
Currently, recipes can be found in one of two places:

1. contained inside the standard sprinter library. Currently the recipes include:

    * git, for git repo cloning
    * unpack, to unpack tar.gz files
    * command, to execute a commnd
    * env, to add environment variables
    * package, to install packages from the package manager of your environment
    * perforce, to configure and install perforce
    * ssh, to set up an ssh key
    * template, to specialize a template and write it to a specified location

2. As a url to a file that contains a python module

e.g:

.. code :: python

  recipe = sprinter.recipe.git
  recipe = http://raw.github.com/toumorokoshi/spriter-recipes/git.py

Standard Recipe Commands
------------------------
Sprinter recipes that extend off of the "RecipeStandard" class come with a series of default actions that can be utilized. These are:

* 'rc': this will add lines into the .rc of your environment, thereby being added to your environment if it's activated. (for setup and updates)
* 'command': this will run the specified command after the recipe is finished (for setup and updates)
