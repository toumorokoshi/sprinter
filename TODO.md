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

General:

* add way to ask for prompts
* cleanly closes bad installs
* rename 'recipes' to 'formula'

Perforce Recipe:

* perforce skipping needs to better
* perforce should prompt for writing password to p4settings (if desired)

SSH Recipe:

* ssh recipe doesn't make .ssh directory (can't repro)

Package Recipe:

* brew functionality (check if brew is functional, error if not)

    * on update, if a package isn't installed, install it again

    


Low Priority:

* Add validator
* catch incomplete format errors
* add ability to source recipes dynamically
* add switch
* add reconfigure command to re-choose values
* check if environment exists before removing, throw message if it doesn't.
* Catch exceptions failsafe
