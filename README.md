sprinter
========

A cross-platform environment bootstrapping framework

Sprinter is a framework designed to making bootstrapping and deployment across machines easier. There are three main components to a usable sprinter script:
* This python egg, to fully utilize the framework
* a sprinter.cfg file, which contains the configuration necessary to install features
* sprinter recipes, which each feature uses as it's instruction manual on how to setup, update, and remove itself 

### Installing sprinter onto a machine permenantly
    (sudo) easy_install sprinter

This will install the sprinter command line to your machine.

Managing multiple sprinter configurations
-----------------------------------------

If you find you need to switch between multiple different sprinter environments, you can do so using the sprinter commmand line with:
sprinter switch MY_ENVIRONMENT

this will look for a .sprinter-MY_ENVIRONMENT folder in your environwent and link everything to there, and deactivate any existing environments


Command list
------------
    $ sprinter install ENVIRONMENT.cfg
Install the environment specifiec in the environment.cfg file. It will update an environment if it already exists.

    $ sprinter activate MY_ENVIRONMENT

Activate MY_ENVIRONMENT

    $ sprinter deaactivate MY_ENVIRONMENT

deactivate MY_ENVIRONMENT

    $ sprinter switch TARGET_ENVIRONMENT

deactivates all other environments and activates TARGET_ENVIRONMENT
