#!/bin/bash
# SET THIS TO YOUR OWN DEST DIR
export MODULE_DEST=`pwd`/py-site-packages/
# python path must include your module dir
export PYTHONPATH="$MODULE_DEST/lib/python2.6/site-packages"
./run_tests.sh
