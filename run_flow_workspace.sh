export PYTHONPATH=$PYTHONPATH:build/lib/
visit -nowin -cli -s setup.py build
visit -cli -s visit_exec_flow_workspace.py "$@"