

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

* Multiple environments can be installed at the same time, with
  different specific names. In this case, we chose to name our
  environment 'myenvironment'
* adding environment configuration through 'features'. a feature is
  decribed by a section in the configuration file (besides
  'config'). In this example, we have two features:

    * 'git', which installs git
    * 'github', which generates an ssh key

Now that's not super difficult, so let's try something more complicated.

`sub <https://github.com/37signals/sub>`_ is a command namespacing tool
that allows the creation of subcommands. (e.g. moving to your
workspace directory or running your server). Let's try adding this to our configuration.

Every feature needs a formula to define what the actual feature is
going to do. sprinter.formula.ssh, as shown above, generates ssh
keys. sprinter.formula.package installs packages from the appropriate
package managers. So how about cloning git repositories? Luckily, sprinter has a formula
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

The git formula clones a git repository into sprinter's directory
(typically ~/.sprinter). In the sub feature, we then evaluate sub's
init script by injecting 'eval "$(%(sub:root_dir)/bin/sub init -)"' into one's .bashrc or .zshrc file.

You can get more information about each of the formulas, and what they
do, on the:ref:`formulas` page.

Now remember at this point, sprinter already knows that you have an
environment 'myenvironment' installed.
Instead of running an install again, you can run an 'update' command on the environment::

    sprinter update myenvironment

The environment 'myenvironment' knows where it found the file last
time, and will record it's location for updating in the
future. Although storing it locally is perfectly fine, it makes more
sense to throw it online somewhere where all of your machines can
access it. as an example, check out github user toumorokoshi's environment configuration file:

https://raw.github.com/toumorokoshi/yt.rc/master/toumorokoshi.cfg


variables in sprinter and referencing other formulas
****************************************************

In the above example, you'll see that you can reference variables and
information about other formulas in the values set. In the 'sub' example,
the value %(sub:root_dir)s in the 'rc' option gets replaced with the directory of the sub feature
during execution. This can make it very easy to perform operations
that rely on information about other features, or the global configuration.

Here's some examples of variables that are set in the above environment:

* %(sub:url)s resolves to git://github.com/mygithub/sub.git
* %(config:namespace)s resolves to 'myenvironment'

Grabbing user input
*******************

Sprinter also provides the capability to prompt the installer for input when installing a sprinter environment. Some common examples are:

* getting a username
* getting passwords for various services
* getting configuration options (version control root directories,
  workspaces)

You can grab user input by adding an 'inputs' option to any
feature. Here's an example of getting a user's username, password, and git root
then using it to make the git root and upload an ssh key through a rest api::

    [config]
    inputs = gitroot==~/git/

    [create_git_root]
    formula = sprinter.formula.command
    install = mkdir -p %(config:gitroot)s
    env = export GITROOT=%(config:gitroot)s

    [stash]
    inputs = username
             githostpassword?
    formula = sprinter.formula.ssh
    depends = curl
    keyname = mygithost.com
    nopassphrase = true
    type = rsa
    user = git
    hostname = mygithost.com
    install_command = curl -k -u '%(config:username)s:%(config:githostpassword)s' -X POST -H "Accept: application/json" -H "Content-Type: application/json" https://mygithost.com/rest/ssh/1.0/keys -d '{"text":"{{ssh}}"}'
    use_global_ssh = False


Note the section 'inputs' has specific syntax::

    gitroot==~/git/  # the == provides a default to the parameter ~/git/
    username   # this is a standard, just asks for a username
    githostpassword?  # the question mark makes it a hidden parameter on input, for passwords and other sensitive data


If you run a sprinter install of this configuration, you would be prompted to enter the variables specified::

    $ sprinter install sshexample.cfg 
    Checking and setting global parameters...
    Installing environment sshexample...
    please enter your gitroot (default ~/git/): 
    please enter your username: 
    please enter your githostpassword: 


All prompted variables in the sprinter configuration are added to the
config section, and can be used with %(config:MYVAR)s. In the example
above, %(config:username)s will resolve to whatever the username
parameter was.

When you update the environment in the future, you don't have to enter
the parameters again. This is because sprinter environments remember
parameters (except passwords/secret parameters. Sprinter stores values
in plaintext, so it's never a good idea to store passwords that
way.). If you want to re-enter parameters, you have to do an update
with a --reconfigure::

    $ sprinter update sshexample --reconfigure

rc and env
**********

If you look at the configuration above, two parameters can be applied
to almost all commands. Those are 'rc' and 'env'. rc and env handle
the actual content that is injected into your shell (e.g. what goes in
your .bashrc or .zshrc). For example, a GoLang installation requires
some environment variables set. You can do so like this::

    [golang-debian]
    systems = debian
    formula = sprinter.formula.unpack
    executable = bin/go
    symlink = go
    remove_common_prefix = true
    url = https://go.googlecode.com/files/go1.1.linux-amd64.tar.gz
    type = tar.gz
    env = export GOROOT=%(golang-debian:root_dir)s
    rc = function gov() {
             go version
         }

(the sprinter.formula.unpack formula handles unpacking of tar.gz, zip,
(and dmg files for OSX)). Here we set an environment variables in
'env', and put functions in 'rc'. This ensures that environment
variables are available for graphical applications, while function are
available for shells.

It's ok not to get into specifics, most of the time just follow these rules:

* environment variables go into 'env'
* everything else goes into 'rc'

What next?
----------

Congratulations! You know a majority of the functionality you need in
sprinter. If you have questions about how to do specific things, try
the FAQ or look at one of the doc pages, or post a question at our
`Google Group <https://groups.google.com/forum/#!forum/sprinter-dev>`_

Also check out the `snippets
<https://github.com/toumorokoshi/sprinter/tree/develop/snippets>`_
section. This is a set of snippets that describe how to install common
things like node.js
