

Sprinter Tutorial
=================

In this tutorial, you will learn:

* How to write a sprinter :term:`manifest` file
* How to ask for user input (username, password, etc)
* How to use user input

Build a sprinter configuration file
-----------------------------------

Each sprinter environment is completely defined by a sprinter configuration file. Think of this file as your main way of managing your sprinter environment: any changes you make here will be picked up next time you update your environment. Here's a good starting point for a sprinter config::

.. Add in sprinter configuration tutorial.cfg

This outlines a lot of the basic functionality that sprinter provides:

* Namespacing an environment (in this case, it's 'mysprinter').
* Using the "inputs" property to get user input we want
    * username asks for the username
    * password? asks for the password, but makes the input hidden (desired for a password field)
* Adding pieces of an environment through 'features', which utilize templates known as recipes. In this example, the 'sub' feature is installed through git, using the 'sprinter.recipes.git' recipe.

Features are the core piece of functionality for sprinter. The way you add or modify what your environment is by adding, removing, and changing the feature configuration in a configuration file.

You can get more information about each of the recipes, and what they do, on the :ref:`recipes` page.

Installing a sprinter environment
---------------------------------

Now, if you want to install this enviroment:

* write the config to a file
* install sprinter::

    $ (sudo) easy_install sprinter

* and install this environment::

    $ sprinter install PATH_TO_MY_CONFIG

So what actually happenned?
