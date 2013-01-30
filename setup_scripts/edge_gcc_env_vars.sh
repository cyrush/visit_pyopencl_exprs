#!/bin/sh
export ROOT=`pwd`
export VISIT_LOC=/usr/gapps/visit
export PATH=$PATH:$VISIT_LOC/bin/
export MODULE_DEST=$ROOT/py-site-packages
export PYTHONPATH="$MODULE_DEST/lib/python2.6/site-packages"
export PYTHONPATH="$PYTHONPATH:$ROOT/flow/build/lib/"
export PYTHONPATH="$PYTHONPATH:$ROOT/visit_flow_vpe/build/lib/"
export LD_LIBRARY_PATH=/usr/gapps/visit/cyrush/NVIDIA-Linux-x86_64-304.32/
