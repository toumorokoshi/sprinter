Environment Name 
-----------------------------
Environment names are ascertained one of two ways. in order of precedence:
* explicitely set via the command line
* explicitely in the config section of the enivronment cfg
* implicitely via the variable name

Sourcing sprinter configs
-------------------------
Sprinter configs can be sourced either via:
* online at a url with a sprinter config
* offline on a disk locally
This is differentiated on the command line with a 'http(s):' located at the beginning.

Injections
----------
Injections are the advised method to modify an environment with sprinter. Injections inject specific content (usually configuration for specific services) into files, and can be removed as well.

* Injections should be called with the 'injections' object in the environment. These are batched up and group injected for you.

* Injections should be modified in the activate/deactivate methods of a recipe.
