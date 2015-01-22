# a one-liner to install a sandboxed sprinter, using uranium (expiremental)
error () {
    last_error=$?
    echo "!!"
    echo $1
    exit $last_error
}

SANDBOX_DIR=/tmp/sprinter-sandbox
if [[ -d $SANDBOX_DIR ]]; then
    rm -r $SANDBOX_DIR
fi

echo "Creating sandbox directory..."
mkdir -p $SANDBOX_DIR
cd $SANDBOX_DIR
echo "Downloading sprinter..."
# install virtualenv
if [[ `uname` == 'Linux' ]]; then
    wget -O sprinter.tar.gz http://github.com/toumorokoshi/sprinter/tarball/master
elif [[ `uname` == 'Darwin' ]]; then
    curl -o sprinter.tar.gz http://github.com/toumorokoshi/sprinter/tarball/master -L
fi
tar -xzvf sprinter.tar.gz --strip-components=1 &> /dev/null || error "Failure extracting sprinter targz!"
echo "Creating python sandbox..."
./uranium --version=0.0.30 || error "Failure with prebuild!"

echo "Removing sprinter environment if it already exists..."
bin/sprinter remove sprinter
if [[ -d ~/.sprinter/sprinter/ ]]; then
    echo "Sprinter environment was not removed cleanly. Forcefully removing..."
    rm -rf ~/.sprinter/sprinter/
fi
echo "Installing global sprinter..."
bin/sprinter install https://raw.github.com/toumorokoshi/sprinter/master/examples/sprinter.cfg || error "Issue installing global sprinter!"

# finally, delete the temporary directory
echo "Cleaning up..."
rm -rf /tmp/sprinter-sandbox || error "Issue cleaning up!"
echo "Done!"
