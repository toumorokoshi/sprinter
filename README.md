sprinter
========
[![Build Status](https://travis-ci.org/toumorokoshi/sprinter.png)](https://travis-ci.org/toumorokoshi/sprinter)

A cross-platform environment bootstrapping framework!

Sprinter is a framework designed to making bootstrapping development environments easier. There are three main components to a usable sprinter script:
* This python egg, to fully utilize the framework
* a sprinter.cfg file, which contains the configuration necessary to install features
* sprinter recipes, which each feature uses as it's instruction manual on how to setup, update, and remove itself 

### Installing sprinter onto a machine permanently
    (sudo) easy_install sprinter

This will install the sprinter command line to your machine. Easy install needs to be installed for now. Conversely, you can use the sandboxer to use sprinter once. (look under examples)

Command list
------------
    $ sprinter install ENVIRONMENT.cfg
    $ sprinter install http://myenvironment.cfg
Install the environment specified in the environment.cfg file. It will update an environment if it already exists.

    $ sprinter activate MY_ENVIRONMENT

Activate MY_ENVIRONMENT

    $ sprinter deaactivate MY_ENVIRONMENT

deactivate MY_ENVIRONMENT

    $ sprinter update MY_ENVIRONMENT

Updates the environment to the latest version as specified in the manifest, and activates it
