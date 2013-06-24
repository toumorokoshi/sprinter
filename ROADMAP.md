Roadmap
-------

TODO:
* Directory behavior changed to warn if a directory is not a symlink, not throw an error.
* test authenticated get catches unauthorized error
* test the 'bash' clause in command

This page highlights Sprinter's roadmap to reach 1.0
release. Currently sprinter is at version 0.4

### 0.6
Remove use of sudo as much as possible

Ensure proper coverage for these modules:

* environment

Test these methods:

General:

* add way to ask for prompts
* cleanly close bad installs

### 0.7
0.7 will focus on how to test formulas. Many bugs will be fixed as well, such as:

Perforce Recipe:

* perforce skipping needs to better
* perforce should install p4v
* perforce should prompt for writing password to p4settings (if desired)

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

### 1.0
Success! A Stable library that can be used to install environments to machines with ease
