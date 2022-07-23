========
sprinter
========

Deprecation!
------------

Note: this package is now deprecated and is not actively updating.

It is currently using and outdated, insecure version of pip (9.0.1). Use at your own risk.

For those interested in an alternative, check out provisioning tools such as Chef (https://chef.io), or
look at https://github.com/toumorokoshi/ytlaces for a similar example in Puppet.

Installation
------------

OSX::

    cd /tmp/; rm sprinter; curl -s https://raw.githubusercontent.com/toumorokoshi/sprinter/master/scripts/sandbox.sh > /tmp/sprinter; bash /tmp/sprinter

Debian-Based (e.g. Ubuntu)::

    cd /tmp/; rm sandbox.sh; wget https://raw.githubusercontent.com/toumorokoshi/sprinter/master/scripts/sandbox.sh -O sandbox.sh; bash sandbox.sh


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


Installing with brewed Python (OS X)
---------------------------
Brewed python (installed via `brew install python`), by default sets a prefix value in ~/.pydistutils.cfg. If this value is set, due to a bug in Python's setup tools, the Sprinter install will fail. To get around this issue do the following.

Remove all traces of brewed python::

    brew uninstall python
    brew uninstall pyenv-virtualenv

Manually move all virtualenv* files under /usr/local/bin to another folder::

    sudo mkdir /usr/local/bin/venv-old
    sudo mv /usr/local/bin/virtualenv* /usr/local/bin/venv-old/

Open a new terminal tab and double-check that you're in a clean state::

    which python # => /usr/bin/python
    which virtualenv # => virtualenv not found

Install Python and virtualenv(wrapper)::

    brew install python --with-brewed-openssl
    # Open a new terminal tab now (to access /usr/local/bin/python)
    pip install virtualenv
    pip install virtualenvwrapper

Original source via stackoverflow: http://stackoverflow.com/questions/16860971/cant-pip-install-virtualenv-in-os-x-10-8-with-brewed-python-2-7
