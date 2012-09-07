#!/bin/sh
export ROOT=`pwd`
export MODULE_DEST=$ROOT/py-site-packages/
export PYTHONPATH="$MODULE_DEST/lib/python2.6/site-packages"
export PYTHONPATH="$PYTHONPATH:$ROOT/flow/build/lib/"
export PYTHONPATH="$PYTHONPATH:$ROOT/visit_flow_vpe/build/lib/"