Highest to Lowest Priority

modules that still need testing:

* directory
* environment
* install
* lib? (double check)
* recipestandard
* manifest? (double check)
* system? (maybe, don't know how to test this)
* recipes (no idea how to test these)

Docs:

* Add doc section for 'phases' and phases keyword in config

General:

* add way to ask for prompts
* cleanly close bad installs

Perforce Recipe:

* perforce skipping needs to better
* perforce should install p4v
* perforce should prompt for writing password to p4settings (if desired)

SSH Recipe:

* ssh recipe doesn't make .ssh directory (can't repro)

Package Recipe:

* brew functionality (check if brew is functional, error if not)

    * on update, if a package isn't installed, install it again

DMG Installation utility:
Create a formula to install the contents of a dmg somewhere, since it seems that a lot of os x utilities use this mechanism.

* Commands to run:
    * hdiutil mount ~/Downloads/P4V.dmg 
    * sudo cp -R /Volumes/P4V/p4v.app /Applications/

* Looks like this would help:
	* http://osxdaily.com/2011/12/17/mount-a-dmg-from-the-command-line-in-mac-os-x/

Low Priority:

* catch incomplete format errors
* add ability to source recipes dynamically
* add switch
* add reconfigure command to re-choose values
* check if environment exists before removing, throw message if it doesn't.
* Catch exceptions failsafe
