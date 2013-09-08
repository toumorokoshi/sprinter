.. Sprinter documentation master file, created by
   sphinx-quickstart on Tue Feb 26 22:15:07 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Sprinter: environment bootstrapping made easy
============================================

Sprinter is a tool to help create environment bootstrapping scripts for developer environments.

Here are some problems that sprinter was designed to solve:

* syncing up personal development environments across computers

    * syncing rc files
    * installing packages
    * configuring systems (e.g. git or ssh configs, setting up the PS1/shell prompt)

* distributing standard development tools and helpers across a company or organization

    * distributing common shell scripts
    * distributing third-party packages
    * distributing internal packages
    * performing strange on-time-setup quirks and workarounds when you
      can't get around to fixing it

* managing multiple development environments on a single machine

    * need to switch between personal and company-specific environment
    * need to switch between environments for open-source projects

Sprinter was designed with modularity, adaption, and cross-compability in mind. Some of the features of sprinter include:

* Installing environments directly from configs on the web
* Updating existing environments
* Managing several environments, activating and deactivating as needed
* Dynamically installing new functionality via formulas
* Sandboxing environments as necessary, such as brew or node.js

Install Instructions
--------------------

Please refer to the `readme <https://github.com/toumorokoshi/sprinter/blob/develop/README.rst>`_ for instructions on installing sprinter.


Compatible Systems
------------------

Sprinter is currently actively developed against the following operating systems:

* OSX
* Ubuntu

And the following shells:

* bash
* zsh

However, Sprinter should work against Debian distributions, and most Ubuntu-based distributions.

Feel free to `make a ticket <https://github.com/toumorokoshi/sprinter/issues?state=open>`_ with
your difficulties with other unix-based operating systems.

There are currently no plans to develop sprinter against non-unix
based operating systems (such as Windows). However, if you're feeling
ambitious, post your thoughts in the `Google Group
<https://groups.google.com/forum/#!forum/sprinter-dev>`_.

Questions?
----------

Try our :doc:`faq`, or post a topic in the
`Google Group
<https://groups.google.com/forum/#!forum/sprinter-dev>`_.

Contents
========

.. toctree::
   :maxdepth: 2

   tutorial
   faq
   examples
   formulalist
   formulas
   manifests
   lifecycle
   internals
   osx
   glossary



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
