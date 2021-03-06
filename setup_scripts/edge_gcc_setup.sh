#!/bin/sh
export MODULE_DEST=`pwd`/py-site-packages
export VISIT_LOC=/usr/gapps/visit
export PATH=$PATH:$VISIT_LOC/bin
# python path must include your module dir
export PYTHONPATH="$MODULE_DEST/lib/python2.6/site-packages"
export CFLAGS="-I/opt/cudatoolkit-4.2/include"
export LDFLAGS="-lOpenCL -L ${VISIT_LOC}/python/2.6.4/linux-x86_64_gcc-4.1/lib"
#export FCOMPILER="intelem"
export BLAS="None"
export LAPACK="None"
export ATLAS="None"
visit -v 2.6.1 -nowin -cli -s  setup_scripts/install_visit_pyopencl_support.py $MODULE_DEST
