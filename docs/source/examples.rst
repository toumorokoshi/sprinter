Sprinter Examples
=================

Here are some cool ways to use sprinter!

Sprinter patterns
-----------------

A good pattern that developers tend to follow is to store all of their
environment rc files (.emacs, .vimrc, etc) in a git repository, and
clone and symlink the result. sprinter can automate that pattern. Look
at this example section below::

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

Installing Sub
--------------

`sub <https://github.com/37signals/sub>`_ is a command namespacing tool
that allows the creation of subcommands. (e.g. moving to your
workspace directory or running your server). This works well with sprinter because:

* sub creates a clear, understandable namespace for shell commands
* sprinter downloads executable and dependencies, and updates the environment needed for those commands

Here's an example sub configuration section::

    [sub]
    formula = sprinter.formulas.git
    depends = github
    url = git://github.com/mygithub/sub.git
    branch = mybranch
    rc = eval "$(%(sub:root_dir)/bin/sub init -)"
