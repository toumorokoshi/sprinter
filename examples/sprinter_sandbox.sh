# a one-liner to install a sandboxed sprinter. Use this if you do not
# want to or can not install sprinter as sudo.
mkdir -p /tmp/sprinter-sandbox
cd /tmp/sprinter-sandbox
#write out the required buildout config file
echo "
[buildout]
parts = python
find-links = http://github.com/toumorokoshi/sprinter/tarball/master#egg=sprinter-0.4.1

[python]
recipe = zc.recipe.egg
include-site-packages = false
eggs = sprinter==0.4.1
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
rm -r /tmp/sprinter-sandbox
