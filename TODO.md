Highest to Lowest Priority

General:

* #_SPRINTER_OVERRIDES section that ensures that sprinter is injected before this
* add way to ask for prompts
* cleanly closes bad installs

Perforce Recipe:

* Prompt for client modification for perforce recipe
* perforce skipping needs to better

SSH Recipe:

* ssh recipe doesn't make .ssh directory (can't repro)

Package Recipe:

* brew functionality (check if brew is functional, error if not)

    * on update, if a package isn't installed, install it again

    


Low Priority:

* Add validator
* catch incomplete format errors
* refactor manifest. very messy right now.
* add ability to source recipes dynamically
* add switch
* add reconfigure command to re-choose values
* check if environment exists before removing, throw message if it doesn't.
* Catch exceptions failsafe
