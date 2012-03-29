#!/bin/sh
WORKSPACE_SCRIPT=`pwd`/"$1"
cd flow && visit -noconfig -nowin -cli -s setup.py build
cd ../
export PYTHONPATH=`pwd`/flow/build/lib/
cd visit_flow_vpe && ./run_workspace.sh $WORKSPACE_SCRIPT
cd ../