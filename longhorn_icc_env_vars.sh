
#module load visit
#export PATH=$PATH:/scratch/01937/cyrush/dev/trunk/src/bin
module swap mvapich2 openmpi
export PATH=/scratch/00401/pnav/visit/openmpi/visit2_4_0.linux-x86_64/bin/:$PATH
module load git
module load cuda cuda_SDK
export PYTHONPATH="/scratch/01937/cyrush/dev/py-site-packages-icc/lib/python2.6/site-packages"
export CFLAGS="-I${TACC_CUDASDK_DIR}/OpenCL/common/inc -no-gcc"
export LDFLAGS="-L${TACC_CUDASDK_DIR}/OpenCL/common/lib -loclUtil_x86_64 -L /scratch/01937/cyrush/libs/2.4.1/python/2.6.4/linux-x86_64_gcc-4.1/lib"
