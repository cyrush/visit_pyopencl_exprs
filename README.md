VisIt pyopencl Expressions Sandbox
================================

This repo will be used to develop support for OpenCL based VisIt expressions.
For initial exploration and prototyping, we will bootstrap OpenCL into VisIt
via pyopencl and VisIt's Python Expression capability.

Getting Started
---------------

1. Install VisIt or setup a development build of the VisIt trunk.
2. Add `visit' to your path (bash examples):

_Standard VisIt Install:_
<pre>
 > export PATH=$PATH:/path/to/visit/bin
</pre>
_OSX Bundle Install:_
<pre>
 > export PATH=$PATH:/path/to/VisIt.app/Contents/Resources/bin
</pre>

3. Clone this repo:
<pre>
 > git clone https://github.com/cyrush/visit_pyopencl_exprs.git
</pre>
4. Install necessary support python modules into VisIt.
Note: You may have to load modules or set env vars to access the OpenCL headers and libs on your system.
To use the NVIDIA OpenCL platform, you will need to load the proper CUDA environment.
<pre>
 > visit -nowin -cli -s install_visit_pyopencl_support.py
</pre>
5. Run module tests for flow & visit_flow_vpe
<pre>
 > ./run_tests.sh
</pre>


How to run example data flow workspaces:
---------------
<pre>
 > ./run_flow_vpe_workspace.sh visit_flow_vpe/examples/flow_vpe_npy_ops_example_1.py
</pre>
<pre>
 > ./run_flow_vpe_workspace.sh visit_flow_vpe/examples/flow_vpe_pyocl_compile_example_1.py
</pre>

How to run the standalone gradient example:
---------------
<pre>
 > cd standalone/gradient/
 > visit -cli -s visit_pyopencl_grad_exec.py
</pre>


Getting Started On Edge
---------------
1. Clone this repo:
<pre>
 > git clone git://github.com/cyrush/visit_pyopencl_exprs.git
</pre>


2. Install necessary support python modules
<pre>
 > ./edge_gcc_setup.sh
</pre>

3. Run tests in an mxterm (to access GPUS)
<pre>
 > mxterm 1 12 30
 [mxterm]> source edge_gcc_env_vars.sh
 [mxterm]> ./run_tests.sh
</pre>

4. Test a single work flow example:
<pre>
 [mxterm]> ./run_flow_vpe_workspace.sh visit_flow_vpe/examples/flow_vpe_pyocl_ops_example_1.py
 (Select 'serial' from the VisIt engine launcher and click 'ok')
</pre>


