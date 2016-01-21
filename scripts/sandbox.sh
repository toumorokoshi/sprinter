# a one-liner to install a sandboxed sprinter, using uranium (expiremental)
error () {
    last_error=$?
    echo "!!"
    echo $1
    exit $last_error
}
INITIAL_DIR=`pwd`

: ${SPRINTER_GITHUB_USER:=toumorokoshi}
: ${SPRINTER_BRANCH:=master}
SANDBOX_DIR=/tmp/sprinter-sandbox
if [[ -d $SANDBOX_DIR ]]; then
    rm -rf $SANDBOX_DIR
fi

echo "Creating sandbox directory..."
mkdir -p $SANDBOX_DIR
cd $SANDBOX_DIR

# install virtualenv
if [ -e $INITIAL_DIR/scripts/sandbox.sh ]; then
    echo "Copying local sprinter";
    cp -R $INITIAL_DIR/* $SANDBOX_DIR
else
    echo "Downloading sprinter..."
    if [[ `uname` == 'Linux' ]]; then
        wget -O sprinter.tar.gz http://github.com/$SPRINTER_GITHUB_USER/sprinter/tarball/$SPRINTER_BRANCH
    elif [[ `uname` == 'Darwin' ]]; then
        curl -o sprinter.tar.gz http://github.com/$SPRINTER_GITHUB_USER/sprinter/tarball/$SPRINTER_BRANCH -L
    fi
    tar -xzvf sprinter.tar.gz --strip-components=1 &> /dev/null || error "Failure extracting sprinter targz!"
fi

echo "Creating python sandbox..."
if [ -n "$URANIUM_PATH" ]; then
    URANIUM_PATH=$INITIAL_DIR/$URANIUM_PATH ./uranium || error "Failure with prebuild!"
else
    ./uranium || error "Failure with prebuild!"
fi
. $SANDBOX_DIR/bin/activate

echo "Removing sprinter environment if it already exists..."
bin/sprinter remove sprinter
if [[ -d ~/.sprinter/sprinter/ ]]; then
    echo "Sprinter environment was not removed cleanly. Forcefully removing..."
    rm -rf ~/.sprinter/sprinter/
fi
echo "Installing global sprinter..."
bin/sprinter install $SANDBOX_DIR/examples/sprinter.cfg || error "Issue installing global sprinter!"

# finally, delete the temporary directory
echo "Cleaning up..."
rm -rf $SANDBOX_DIR || error "Issue cleaning up!"
echo "Done!"
