Sprinter Internals
==================

This page discusses the internals of a sprinter environment. Specifically, the building blocks that constitutes a sprinter environment.

Environment activation/deactivation
-----------------------------------

The main tool that environments are activated and deactivated is through "injections" of text into various configuration files on a client machine. A common injections that occurs is injecting the .rc file for an environment into a .bashrc/.bash_profile like so::

   #sprinter-ENVIRONMENT
   inject environment
   #sprinter-ENVIRONMENT    

Injections can be performed on any set of files that exist with an environment. An example of common ones are:

* the .ssh/config file
* .pypirc for local repositories
* .vimrc for fim configuration
* .emacs for emacs configuration

And more! Any file can have configuration injected, which should be removed in the activate/deactivate step.


The .rc file
^^^^^^^^^^^^

Every sprinter environment has a .rc file at it's core. Identical in concept to a .bashrc or .bash_profile, this .rc file contains a majority of the configuration of the setup for an environment.

The .sprinter-ENVIRONMENT directory
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A majority of the files required for a sprinter environment are stored in a .sprinter-ENVIRONMENT directory within 

Features
^^^^^^^^

Each section in a sprinter configuration represents a "feature", which exists in a particular state. Each service is dealt with separately, and is designed a service directory within the configuration root that it can use to place whatever it would like (clone a git repository, unpack a package, etc).
