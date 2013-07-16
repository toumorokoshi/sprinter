# a one-liner to install a sandboxed sprinter. Use this if you do not
# want to or can not install sprinter as sudo.
# this is also a great example of creating a standalone installer for an environment
mkdir -p /tmp/sprinter-sandbox
cd /tmp/sprinter-sandbox
# install virtualenv
if [[ `uname` == 'Linux' ]]; then
    wget https://raw.github.com/toumorokoshi/sprinter/master/sprinter/virtualenv.py
elif [[ `uname` == 'Darwin' ]]; then
    curl -o virtualenv.py https://raw.github.com/toumorokoshi/sprinter/master/sprinter/virtualenv.py
fi
python virtualenv.py sprinter-dir
cd sprinter-dir
bin/easy_install http://github.com/toumorokoshi/sprinter/tarball/master
 
# Put your Commands here. e.g.:
bin/sprinter install https://raw.github.com/toumorokoshi/sprinter/master/examples/sprinter.cfg
 
 
# finally, delete the temporary directory
rm -r /tmp/sprinter-sandbox
