.. Sprinter documentation master file, created by
   sphinx-quickstart on Tue Feb 26 22:15:07 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Sprinter's documentation!
====================================

Sprinter is a tool to help create environment bootstrapping scripts for developer environments.

Sprinter was designed with modularity, adaption, and cross-compability in mind. Some of the features of sprinter include:

* Installing environments directly from configs on the web
* Updating existing environments
* Managing several environments, activating and deactivating as needed
* Sandboxing common package managers such as brew and easy_install

To Install: ::

  $ (sudo) easy_install sprinter

In your console. Alternatively, a sandboxed version of sprinter
exists, which will install a sprinter environment containing
sprinter. (Holy recursion, Batman!). You can do this with the following one-liner:

OSX::

    $ curl -s https://raw.github.com/toumorokoshi/sprinter/master/examples/sprinter_sandbox.sh > /tmp/sprinter; bash /tmp/sprinter

Debian-Based (e.g. Ubuntu)::
    
    $ cd /tmp/; wget https://raw.github.com/toumorokoshi/sprinter/master/examples/sprinter_sandbox.sh; bash sprinter_sandbox.sh

Compatible Systems
------------------

Sprinter is currently actively developed against the following:

* OSX
* Ubuntu

However, Sprinter should work against Debian distributions, and most Ubuntu-based distributions.

Feel free to `make a ticket <https://github.com/toumorokoshi/sprinter/issues?state=open>`_ with
your difficulties with other unix-based operating systems.

There are currently no plans to develop sprinter against non-unix based operating systems.

Contents
========

.. toctree::
   :maxdepth: 2

   tutorial
   faq
   formulas
   manifests
   lifecycle
   internals
   glossary



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

