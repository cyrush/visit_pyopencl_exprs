#!/bin/sh
export MODULE_DEST=`pwd`/py-site-packages/
export VISIT_LOC="/work/00401/pnav/visit"
export OPENCL_LOC="/opt/apps/intel/opencl/3.0"
export PATH=$PATH:$VISIT_LOC/trunk/src/bin:${OPENCL_LOC}/bin
# python path must include your module dir
export PYTHONPATH="$MODULE_DEST/lib/python2.6/site-packages"
export CFLAGS="-I${OPENCL_LOC}/include"
export LDFLAGS="-L${OPENCL_LOC}/lib64 -L${VISIT_LOC}/visit/python/2.6.4/linux-x86_64_icc/lib"
#export FCOMPILER="intelem"
export BLAS="None"
export LAPACK="None"
export ATLAS="None"
visit -nowin -cli -s install_visit_pyopencl_support.py $MODULE_DEST
