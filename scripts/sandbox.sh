# a one-liner to install a sandboxed sprinter. Use this if you do not
# want to or can not install sprinter as sudo.
# this is also a great example of creating a standalone installer for an environment
error () {
    last_error=$?
    echo $1;
    exit $last_error
}

echo "Creating sandbox directory..."
mkdir -p /tmp/sprinter-sandbox
cd /tmp/sprinter-sandbox
echo "Creating python sandbox..."
# install virtualenv
if [[ `uname` == 'Linux' ]]; then
    wget https://raw.github.com/toumorokoshi/sprinter/master/sprinter/external/virtualenv.py
elif [[ `uname` == 'Darwin' ]]; then
    curl -o sprinter.tar.gz http://github.com/toumorokoshi/sprinter/tarball/master -L
fi
tar -xzvf sprinter.tar.gz --strip-components=1 &> /dev/null || error "Failure extracting sprinter targz!"
python bootstrap.py || error "Failure with bootstrap.py!"
echo "Installing sprinter to sandbox..."
bin/buildout -c buildout-install.cfg &> /dev/null || error "Failure with buildout!"
 
echo "Removing sprinter environment if it already exists..."
bin/sprinter remove sprinter || error "Failure removing sprinter!"
if [[ -d ~/.sprinter/sprinter/ ]]; then
    echo "Sprinter environment was not removed cleanly. Forcefully removing..."
    rm -rf ~/.sprinter/sprinter/ || error "Failure forcefully removing sprinter!"
fi
echo "Installing global sprinter..."
bin/sprinter install https://raw.github.com/toumorokoshi/sprinter/master/examples/sprinter.cfg || error "Issue installing global sprinter!"
 
# finally, delete the temporary directory
echo "Cleaning up..."
rm -r /tmp/sprinter-sandbox || error "Issue cleaning up!"
echo "Done!"
