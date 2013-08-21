

Sprinter Tutorial
=================

In this tutorial, you will learn:

* How to write a sprinter :term:`manifest` file
* How to ask for user input (username, password, etc)
* How to use user input


Installation
------------

First, you need to install sprinter. You can find install instructions in the sprinter readme
`here <https://github.com/toumorokoshi/sprinter/blob/develop/README.rst>`_.


Build a sprinter configuration file
-----------------------------------

Each sprinter environment is completely defined by a sprinter
configuration file. Think of this file as your main way of managing
your sprinter environment: any changes you make here will be picked up
next time you update your environment. Here's a good starting point
for a sprinter config::

    [config]
    namespace = myenvironment

    [git]
    formula = sprinter.formula.package
    apt-get = git-core
    brew = git

    [github]
    formula = sprinter.formula.ssh
    keyname = github.com
    nopassphrase = true
    type = rsa
    host = github.com
    user = git
    hostname = github.com

What does this do? Well, give it a shot! Write this to a file called
myenvironment.cfg (you should replace myenvironment with your username
or whatever makes sense to describe your own personal environment), and install it with:

    sprinter install myenvironment.cfg

When you run the above command, you will first be prompted to configure sprinter if you haven't already.

The next thing sprinter will do is install the 'myenvironment' environment. As defined above, this consists of:

* install brew if you don't have it already (OSX Users)
* use brew or apt-get to install git
* create an ssh key just for github, and add it to the ssh
  configuration file

Now you just add the ssh key to github, and you're done! (you can find
the path to the ssh file in your ~/.ssh/config file) (Unfortunately
it's not possible to add the key to github programatically)

.. Add in sprinter configuration tutorial.cfg

This outlines a lot of the basic functionality that sprinter provides:

* Namespacing an environment (in this case, it's 'myenvironment').
* adding environment configuration through 'features'. In this example, we have two features:

    * 'git', which installs git
    * 'github', which generates an sshkey and sets up the git configuration

Now that's not super difficult, so let's try something more complicated.

`sub <https://github.com/37signals/sub>`_ is a command namespacing tool
that allows the creation of subcommands. (e.g. moving to your
workspace directory or running your server). Let's try adding this to our configuration.

Every feature needs a formula to define what the actual feature is
going to do. sprinter.formula.ssh, as show above, generates ssh
keys. sprinter.formula.package, install packages from the appropriate
package managers. So how about git? Luckily, sprinter has a formula
for this as well: sprinter.formula.git. We can add a new feature by
adding it's configuration into the environment config. We'll add a
section to myenvironment.cfg now::

    [config]
    namespace = myenvironment

    [git]
    formula = sprinter.formula.package
    apt-get = git-core
    brew = git

    [github]
    formula = sprinter.formula.ssh
    keyname = github.com
    nopassphrase = true
    type = rsa
    host = github.com
    user = git
    hostname = github.com

    [sub]
    formula = sprinter.formulas.git
    depends = github
    url = git://github.com/mygithub/sub.git
    branch = mybranch
    rc = eval "$(%(sub:root_dir)/bin/sub init -)"

You can get more information about each of the formulas, and what they
do, on the:ref:`formulas` page.

variables in sprinter and referencing other formulas
****************************************************

Note that here, you'll see that you can reference variables and
information about other formulas in the config. In the 'sub' example,
the rc value %(sub:root_dir)s gets replaced with the directory of the sub feature
during execution. This can make it very easy to perform operations
that rely on information about other formulas.

Here's some examples of variables that are set in the above environment:

* %(sub:url)s resolves to git://github.com/mygithub/sub.git

Now remember at this point, sprinter already knows that you have an
environment 'myenvironment' installed.
Instead of running an install again, you can run an 'update' command on the environment::

    sprinter update myenvironment

The environment 'myenvironment' knows where it found the file last
time, and will record it's location for updating in the
future. Although storing it locally is perfectly fine, it makes more
sense to throw it online somewhere where all of your machines can
access it. as an example, check out github user toumorokoshi's configuration:

https://raw.github.com/toumorokoshi/yt.rc/master/toumorokoshi.cfg

A good pattern that developers tend to follow is to store all of their environment rc files (.emacs, .vimrc, etc) in a git repository, and clone and symlink the result. sprinter can automate that pattern. Look at this example section below::

    [ytrc]
    formula = sprinter.formula.git
    depends = github,git
    url = git://github.com/toumorokoshi/yt.rc.git
    command =
        rm $HOME/.vimrc
        ln -s %(ytrc:root_dir)s/.vimrc $HOME/.vimrc
        rm $HOME/.screenrc
              ln -s %(ytrc:root_dir)s/.screenrc $HOME/.screenrc
        rm $HOME/.emacs.d
              ln -s %(ytrc:root_dir)s/emacs $HOME/.emacs.d
        rm $HOME/.viper
              ln -s %(ytrc:root_dir)s/.viper $HOME/.viper
        rm $HOME/.emacs
              ln -s %(ytrc:root_dir)s/emacs/.emacs $HOME/.emacs
        rm $HOME/.tmux.conf
              ln -s %(ytrc:root_dir)s/.tmux.conf $HOME/.tmux.conf
    rc = . %(ytrc:root_dir)s/rc

