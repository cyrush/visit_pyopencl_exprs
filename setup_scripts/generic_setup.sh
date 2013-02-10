#!/bin/bash
# SET THIS TO YOUR OWN DEST DIR
export MODULE_DEST="/work/visit/trunk/test-build/visit/virtualenv/"
# python path must include your module dir
export PYTHONPATH="$MODULE_DEST/lib/python2.7/site-packages"

visit -nowin -cli -s setup_scripts/install_visit_pyopencl_support.py $MODULE_DEST
