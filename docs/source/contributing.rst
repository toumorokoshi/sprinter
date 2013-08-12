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

*NOTE* It is not reccomended to maintain state within an
 object. (e.g. defining a variable self.myvar in the prompt method and
 then using it in the install method). Although this may work
 currently, there is no specification that dictates that the order on
 which methods are called against an object will be constant.

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
