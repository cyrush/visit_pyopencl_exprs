#!/bin/sh
export ROOT=`pwd`
export MODULE_DEST="/work/visit/trunk/test-build/visit/virtualenv/" #$ROOT/py-site-packages/
export PYTHONPATH="$MODULE_DEST/lib/python2.7/site-packages"
export PYTHONPATH="$PYTHONPATH:$ROOT/flow/build/lib/"
export PYTHONPATH="$PYTHONPATH:$ROOT/visit_flow_vpe/build/lib/"
