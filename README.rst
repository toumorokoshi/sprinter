========
sprinter
========


.. image:: https://travis-ci.org/toumorokoshi/sprinter.png
   :alt: build status

Installation
------------
You can install sprinter using easy_install::

    $ (sudo) easy_install http://github.com/toumorokoshi/sprinter/tarball/master

Or use a sandboxed install:

OSX::

    $ curl -s https://raw.github.com/toumorokoshi/sprinter/master/examples/sprinter_sandbox.sh > /tmp/sprinter; bash /tmp/sprinter

Debian-Based (e.g. Ubuntu)::
    
    $ cd /tmp/; wget https://raw.github.com/toumorokoshi/sprinter/master/examples/sprinter_sandbox.sh; bash sprinter_sandbox.sh
   

A cross-platform environment bootstrapping framework!

Sprinter is a framework designed to making bootstrapping development
environments easier. There are three main components to a usable
sprinter script:

* This python egg, to fully utilize the framework
* a sprinter.cfg file, which contains the configuration necessary to install features
* sprinter recipes, which each feature uses as it's instruction manual on how to setup, update, and remove itself 

This will install the sprinter command line to your machine. Easy
install needs to be installed for now. Conversely, you can use the
sandboxer to use sprinter once. (look under examples)

Command list
------------

Install an environment::

  $ sprinter install ENVIRONMENT.cfg
  $ sprinter install http://myenvironment.cfg

Install the environment specified in the environment.cfg file. It will update an environment if it already exists.::

    $ sprinter activate MY_ENVIRONMENT

Activate MY_ENVIRONMENT::

    $ sprinter deaactivate MY_ENVIRONMENT

deactivate MY_ENVIRONMENT::

    $ sprinter update MY_ENVIRONMENT

remove MY_ENVIRONMENT::

    $ sprinter remove MY_ENVIRONMENT
