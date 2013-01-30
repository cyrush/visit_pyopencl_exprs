#!/bin/bash
# SET THIS TO YOUR OWN DEST DIR
export MODULE_DEST=`pwd`/py-site-packages/
# python path must include your module dir
export PYTHONPATH="$MODULE_DEST/lib/python2.6/site-packages"
visit -nowin -cli -s setup_scripts/install_visit_pyopencl_support.py $MODULE_DEST
