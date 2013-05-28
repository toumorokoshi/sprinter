Roadmap
-------

This page highlights Sprinter's roadmap to reach 1.0
release. Currently sprinter as at version 0.4

### 0.5
Remove use of sudo as much as possible

Ensure proper coverage for these modules:

* directory
* environment
* install
* lib? (double check)
* recipestandard
* manifest? (double check)
* system? (maybe, don't know how to test this)

Test these methods:

General:

* add way to ask for prompts
* cleanly close bad installs

### 0.6 
0.6 will focus on how to test formulas. Many bugs will be fixed as well, such as:

Perforce Recipe:

* perforce skipping needs to better
* perforce should install p4v
* perforce should prompt for writing password to p4settings (if desired)

SSH Recipe:

* ssh recipe doesn't make .ssh directory (can't repro)

Package Recipe:

* brew functionality (check if brew is functional, error if not)

    * on update, if a package isn't installed, install it again


### 0.8
Bugfix release:
Low Priority:

* catch incomplete format errors
* add ability to source recipes dynamically
* add switch
* add reconfigure command to re-choose values
* check if environment exists before removing, throw message if it doesn't.
* Catch exceptions failsafe


### 0.9 
The documentation needs to properly and completely document
the sprinter libraries and extension design:

* Add doc section for 'phases' and phases keyword in config
