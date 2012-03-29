#!/bin/sh
#
# ${disclaimer}
#
# file: run_workspace.sh
# author: Cyrus Harrison <cyrush@llnl.gov>
# created: 3/25/20112
# description:
#   Helper script for executing flow workspaces.
#
#   Usage:
#    ./run_workspace.sh examples/flow_npy_compile_example_1.py
#
python setup.py build
export PYTHONPATH=$PYTHONPATH:build/lib/
python "$@"
