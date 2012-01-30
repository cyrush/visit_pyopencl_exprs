#!/bin/bash
module load git
module load cuda cuda_SDK
# SET THIS TO YOUR OWN DEST DIR
export MODULE_DEST=/scratch/01937/cyrush/dev/py-site-packages/
# make sure the proper dir structure exists, or 'distribute' will complain & give up
mkdir $MODULE_DEST
mkdir $MODULE_DEST/lib
mkdir $MODULE_DEST/lib/python2.6
mkdir $MODULE_DEST/lib/python2.6/site-packages
# set this to your own visit loc, or use my dev build
export VISIT_LOC=/scratch/01937/cyrush/dev/trunk/src/bin
export PATH=$PATH:$VISIT_LOC
# python path must include your module dir
export PYTHONPATH="$MODULE_DEST/lib/python2.6/site-packages"
export CFLAGS="-I${TACC_CUDASDK_DIR}/OpenCL/common/inc"
export LDFLAGS="-L${TACC_CUDASDK_DIR}/OpenCL/common/lib -loclUtil_x86_64 -L /scratch/01937/cyrush/libs/2.4.1/python/2.6.4/linux-x86_64_gcc-4.1/lib"
visit -nowin -cli -s install_visit_pyopencl_support.py $MODULE_DEST
