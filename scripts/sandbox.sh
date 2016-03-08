# a one-liner to install a sandboxed sprinter, using uranium (expiremental)
error () {
    last_error=$?
    echo "!!"
    echo $1
    exit $last_error
}
INITIAL_DIR=`pwd`

: ${SPRINTER_GITHUB_ACCOUNT:=toumorokoshi}
: ${SPRINTER_GITHUB_BRANCH:=master}
: ${SPRINTER_ENV_ROOT:=$HOME/.sprinter}
SANDBOX_DIR=/tmp/sprinter-sandbox-`whoami`
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
        wget -O sprinter.tar.gz http://github.com/$SPRINTER_GITHUB_ACCOUNT/sprinter/tarball/$SPRINTER_GITHUB_BRANCH
    elif [[ `uname` == 'Darwin' ]]; then
        curl -o sprinter.tar.gz http://github.com/$SPRINTER_GITHUB_ACCOUNT/sprinter/tarball/$SPRINTER_GITHUB_BRANCH -L
    fi
    tar -xzvf sprinter.tar.gz --strip-components=1 &> /dev/null || error "Failure extracting sprinter targz!"
fi

echo "Creating python sandbox..."
if [ -n "$URANIUM_PATH" ]; then
    URANIUM_PATH=$INITIAL_DIR/$URANIUM_PATH ./uranium || error "Failure with prebuild!"
else
    ./uranium || error "Failure with prebuild!"
fi

echo "Removing sprinter environment if it already exists..."
bin/sprinter remove sprinter
if [[ -d $SPRINTER_ENV_ROOT/sprinter/ ]]; then
    echo "Sprinter environment was not removed cleanly. Forcefully removing..."
    rm -rf $SPRINTER_ENV_ROOT/sprinter/
fi
echo "Installing global sprinter..."
bin/sprinter install $SANDBOX_DIR/examples/sprinter.cfg || error "Issue installing global sprinter!"

# finally, delete the temporary directory
echo "Cleaning up..."
rm -rf $SANDBOX_DIR || error "Issue cleaning up!"
echo "Done!"
