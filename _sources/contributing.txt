Formula Guidelines
==================

Sprinter provides a lot of flexibility for a variety of use
cases. This page will hopefully explain some the more hidden, nuanced
factors and functionality in writing formulas.


Prompting for values
--------------------

There are two accepted ways to prompt users for values:

* using the reserved 'input' keyword in a formula to define inputs
* overriding the 'prompt' method in formulabase

The 'input' keyword should be used for values that are always needed
(such as a username/password for version control). The prompt method
should be used for optional configuration or for configuration based
up on the system being installed (such as overwriting existing values)

*NOTE* The only way to share state between phases is through
 configuration. A new instance of an object is instantiated for every
 method every time, so it is not possible to save state between say,
 the prompt method and the update method later on.

Config behaviour
----------------

*Config Resolution* for any values in the 'config' section of the
manifest, the target manifest will override source manifest values. This
includes:

    * Values obtained from user input

*Feature Config Resolution* Config resolution for a particular feature
is dictated by the formula's static 'resolve' method, but this
typically utilizes the base classes resolution method, which is target
overriding source values explicitely referenced. Any values that are
not in the target feature config are left alone.
