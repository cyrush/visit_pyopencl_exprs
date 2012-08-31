#!/bin/sh
export MODULE_DEST=`pwd`/py-site-packages/
export VISIT_LOC=/usr/gapps/visit/
export PATH=$PATH:$VISIT_LOC/bin/
export PYTHONPATH="$MODULE_DEST/lib/python2.6/site-packages"
export LD_LIBRARY_PATH=/usr/gapps/visit/cyrush/NVIDIA-Linux-x86_64-304.32/
