#!/bin/sh
export ROOT=`pwd`
export VISIT_LOC="/work/00401/pnav/visit/trunk/src"
export OPENCL_LOC="/opt/apps/intel/opencl/3.0"
export PATH=$PATH:$VISIT_LOC/bin:${OPENCL_LOC}/bin
# python path must include your module dir
export PYTHONPATH="$MODULE_DEST/lib/python2.6/site-packages"
export MODULE_DEST=$ROOT/py-site-packages/
export PYTHONPATH="$MODULE_DEST/lib/python2.6/site-packages"
export PYTHONPATH="$PYTHONPATH:$ROOT/flow/build/lib/"
export PYTHONPATH="$PYTHONPATH:$ROOT/visit_flow_vpe/build/lib/"
