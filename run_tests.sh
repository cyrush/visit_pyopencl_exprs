#!/bin/sh
cd flow && visit -noconfig -nowin -cli -s setup.py test
cd ../
export PYTHONPATH=$PYTHONPATH:`pwd`/flow/build/lib/
cd visit_flow_vpe && visit -noconfig -nowin -cli -s setup.py test
