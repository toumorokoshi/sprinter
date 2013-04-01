# a one-liner to setup a sandboxed sprinter and perform a sprinter
# command use this if you do not want to install sprinter globally,
# and prefer a one-time use instead.
TMP="$(mktemp -d)"
cd $TMP
write out the required buildout config file
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
    curl http://downloads.buildout.org/2/bootstrap.py
fi
python bootstrap.py
bin/buildout


# put your commands here. e.g.:
# sprinter install https://raw.github.com/toumorokoshi/yt.rc/master/toumorokoshi.cfg


# finally, delete the temporary directory
rm -r $TMP
