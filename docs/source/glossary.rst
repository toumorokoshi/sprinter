Glossary
========

.. glossary::

  environment 
    An environment in the sprinter context is a collection
    of :term:`features <feature>` for a client machine that can be
    described by a sprinter manifest file. Sprinter's main job is to
    install, update, and ultimately manages these environments.

  feature 
    A sprinter feature represents a single unit of configuration
    for a sprinter environment. A feature should represent a single
    modular, functional unit to manage one aspect of an environment,
    such as the environment variables, a package that needs to be
    installed, or an in-house command line tool.

  formula 
    A formula represents a classification of a feature, that
    provides the steps to install, update, etc. a feature.

  manifest 
    A sprinter manifest is a configuration file describing a
    sprinter :term:`environment`. Sprinter manifest examples can be
    found in the source code, or in the :doc:`tutorial`.

  .rc file 
    The file that is :term:`injected <injection>` into the
    .bashrc or shell's rc for the client. This performs the
    majority of the activation and deactivation of a sprinter
    environment. More information can be found at :doc:`internals`.

  .env file 
    The file that is :term:`injected <injection>` into the
    graphical environment or shell profile on the client. Similar to the .rc file,
    this is intended for configuration that specifically affects the
    client and not specific functionlity for a interactive shell
    (e.g. environment variables instead of shell functions) majority
    of the activation and deactivation of a sprinter environment. More
    information can be found at :doc:`internals`.

  injection 
    An injection is when sprinter-specific configuration is
    inserted into an existing configuration file on a client. More
    informmation can found at :doc:`internals`.
