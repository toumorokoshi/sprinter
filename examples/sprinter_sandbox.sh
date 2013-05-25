# a one-liner to setup a sandboxed sprinter and perform a sprinter
# command use this if you do not want to install sprinter globally,
# and prefer a one-time use instead.
TMP="$(mktemp -d)"
cd $TMP
#write out the required buildout config file
echo "
[buildout]
parts = python

[python]
recipe = zc.recipe.egg
eggs = sprinter
" > buildout.cfg
# install buildout sandboxed
if [[ `uname` == 'Linux' ]]; then 
    wget http://downloads.buildout.org/2/bootstrap.py
elif [[ `uname` == 'Darwin' ]]; then
    curl -o bootstrap.py http://downloads.buildout.org/2/bootstrap.py
fi
python bootstrap.py
bin/buildout


# Put your Commands here. e.g.:
bin/sprinter install https://raw.github.com/toumorokoshi/sprinter/master/examples/sprinter.cfg


# finally, delete the temporary directory
rm -r $TMP
