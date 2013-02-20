Environment Name 
-----------------------------
Environment names are ascertained one of two ways. in order of precedence:
* explicitely set via the command line
* explicitely in the config section of the enivronment cfg
* implicitely via the variable name

Sourcing sprinter manifests
---------------------------
Sprinter manifests can be sourced either via:
* online at a url with a sprinter config
* offline on a disk locally
This is differentiated on the command line with a 'http(s):' located at the beginning.

Injections
----------
Injections are the advised method to modify an environment with sprinter. Injections inject specific content (usually configuration for specific services) into files, and can be removed as well.

* Injections should be called with the 'injections' object in the environment. These are batched up and group injected for you.

* Injections should be modified in the activate/deactivate methods of a recipe in addition to setup and update

manifest [config] section
-------------------------
The config section of a manifest holds special meaning, as it is the section where various values regarding user or instance-specific installs are stored. There are also a couple of keys reserved for specific purposes. Those are:
* source : this is populated automatically by sprinter, and it references the original locations of where the manifest was retrieved. Sprinter references this location when an update is called.


Standard recipe parameters
--------------------------
The following are a list of standard recipe parameters that provide actions:

* command: command starts a subshell and executes the process.
* inputs : inputs is a newline-delimited list of values that signifies that user input is required. these values will be requested at the beginning of a fresh manifest install. On updates or subsequent installs, only new values will be asked for.
* rc: rc will inject a string of text (parameter specialized) into the sprinterrc file, which is sourced on activation of the environment.


Input syntax
------------
Inputs are newline-delimited, and has a couple of optional parameters. These parameters are:

* a succeeding == with a parameter is the default for the parameter: (sprinter_temp==/tmp/)
* a question mark after the param name means it is temporary - it implies it should be a hidden config, such as a password. (password?)
