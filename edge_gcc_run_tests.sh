#!/bin/sh
export MODULE_DEST=/g/g24/cyrush/work/visit_pyopencl_exprs/py-site-packages/
# set this to your own visit loc, or use my dev build
export VISIT_LOC=/usr/gapps/visit/bin/
export PATH=$PATH:$VISIT_LOC/bin/
# python path must include your module dir
export PYTHONPATH="$MODULE_DEST/lib/python2.6/site-packages"
./run_tests.sh
