#!/bin/bash
module load visit
module load git
module load cuda cuda_SDK
# SET THIS TO YOUR OWN DEST DIR
export MODULE_DEST=/scratch/01937/cyrush/dev/py-site-packages-icc/
# set this to your own visit loc, or use my dev build
#export VISIT_LOC=/scratch/01937/cyrush/dev/trunk/src/bin
#export PATH=$PATH:$VISIT_LOC
# python path must include your module dir
export PYTHONPATH="$MODULE_DEST/lib/python2.6/site-packages"
export CFLAGS="-I${TACC_CUDASDK_DIR}/OpenCL/common/inc -no-gcc"
export LDFLAGS="-L${TACC_CUDASDK_DIR}/OpenCL/common/lib -loclUtil_x86_64 -L /opt/apps/intel11_1/mvapich2_1_4/visit/2.4.0/linux-x86_64/lib/"
visit -nowin -cli -s  setup_scripts/install_visit_pyopencl_support.py $MODULE_DEST
