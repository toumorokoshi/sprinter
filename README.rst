========
sprinter
========


.. image:: https://travis-ci.org/toumorokoshi/sprinter.png
   :alt: build status
   :target: https://travis-ci.org/toumorokoshi/sprinter

.. image:: https://d2weczhvl823v0.cloudfront.net/toumorokoshi/sprinter/trend.png
   :alt: Bitdeli badge
   :target: https://bitdeli.com/free

Installation
------------

It's recommended to use Sprinter's standalone installer:

OSX::

    curl -s https://raw.github.com/toumorokoshi/sprinter/master/scripts/sandbox.sh > /tmp/sprinter; bash /tmp/sprinter

Debian-Based (e.g. Ubuntu)::
    
    cd /tmp/; rm sandbox.sh; wget https://raw.github.com/toumorokoshi/sprinter/master/scripts/sandbox.sh -O sandbox.sh; bash sandbox.sh
   

You can also install sprinter using easy_install or pip (not recommended, it's easier to update with the standalone)::

    (sudo) easy_install http://github.com/toumorokoshi/sprinter/tarball/master

    (sudo) pip install http://github.com/toumorokoshi/sprinter/tarball/master

What is it?
-----------

A cross-platform environment bootstrapping framework!

Sprinter is a framework designed to making bootstrapping development
environments easier. There are three main components to a usable
sprinter environment:

* This python egg, to fully utilize the framework
* a sprinter.cfg file, which contains the configuration necessary to install features
* sprinter formulas, which each feature uses as it's instruction manual on how to setup, update, and remove itself 

Read more about Sprinter on the `docs <http://sprinter.readthedocs.org/en/latest/>`_

Command list
------------

Install an environment::

  sprinter install ENVIRONMENT.cfg
  sprinter install http://myenvironment.cfg

Install the environment specified in the environment.cfg file. It will update an environment if it already exists.::

    sprinter update MY_ENVIRONMENT

Activate MY_ENVIRONMENT::

    sprinter activate MY_ENVIRONMENT

deactivate MY_ENVIRONMENT::

    sprinter deactivate MY_ENVIRONMENT

remove MY_ENVIRONMENT::

    sprinter remove MY_ENVIRONMENT
