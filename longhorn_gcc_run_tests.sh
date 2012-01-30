#!/bin/bash
module load cuda cuda_SDK
# SET THIS TO YOUR OWN DEST DIR
export MODULE_DEST=/scratch/01937/cyrush/dev/py-site-packages/
# set this to your own visit loc, or use my dev build
export VISIT_LOC=/scratch/01937/cyrush/dev/trunk/src/bin
export PATH=$PATH:$VISIT_LOC
# python path must include your module dir
export PYTHONPATH="$MODULE_DEST/lib/python2.6/site-packages"
./run_tests.sh
