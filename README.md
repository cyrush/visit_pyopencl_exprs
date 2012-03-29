VisIt pyopencl Expressions Sandbox
================================

This repo will be used to develop support for OpenCL based VisIt expressions.
For initial exploration and prototyping, we will bootstrap OpenCL into VisIt
via pyopencl and VisIt's Python Expression capability.

Getting Started
---------------

1. Install VisIt 2.4.0 or setup a development build of the VisIt trunk.  
[VisIt 2.4.0 Release Binaries](http://portal.nersc.gov/svn/visit/trunk/releases/2.4.0/)  
[VisIt 2.4.0 OSX 64-bit Bundle](http://portal.nersc.gov/svn/visit/trunk/releases/2.4.0/VisIt-2.4.0-x86_64-installer.dmg)  
2. Add `visit' to your path (bash examples):


_Standard VisIt Install:_
<pre>
 > export PATH=$PATH:/path/to/visit/bin
</pre>
_OSX Bundle Install:_  
<pre>
 > export PATH=$PATH:/path/to/VisIt.app/Contents/MacOS/
</pre>

3. Clone this repo:
<pre>
 > git clone https://github.com/cyrush/visit_pyopencl_exprs.git
</pre>
4. Install necessary support python modules into VisIt
<pre>
 > visit -nowin -cli -s install_visit_pyopencl_support.py
</pre>
5. Run module tests for flow & visit_flow_vpe
<pre>
 > ./run_tests.sh
</pre>

6. Run the example flow workspaces
<pre>
 > ./run_flow_vpe_workspace.sh visit_flow_vpe/examples/flow_vpe_npy_ops_example_1.py 
</pre>
<pre>
 > ./run_flow_vpe_workspace.sh visit_flow_vpe/examples/flow_vpe_pyocl_compile_example_1.py
</pre>

Running standalone gradient example:
---------------
<pre>
 > cd standalone/gradient/
 > visit -cli -s visit -cli -s visit_pyopencl_grad_exec.py 
</pre>
 

