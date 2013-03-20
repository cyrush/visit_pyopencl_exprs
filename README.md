VisIt pyopencl Expressions Sandbox
================================

This repo will be used to develop support for OpenCL based VisIt expressions.
For initial exploration and prototyping, we will bootstrap OpenCL into VisIt
via pyopencl and VisIt's Python Expression capability.

Getting Started
---------------

1) Install VisIt or setup a development build of the VisIt trunk.
<pre>
VisIt Release Binaires:  https://wci.llnl.gov/codes/visit/executables.html
VisIt Trunk Anonymous SVN: http://portal.nersc.gov/svn/visit/trunk/src/
</pre>

2) Add _visit_ to your path (bash examples):

_Standard VisIt Install:_
<pre>
 > export PATH=$PATH:/path/to/visit/bin
</pre>
_OSX Bundle Install:_
<pre>
 > export PATH=$PATH:/path/to/VisIt.app/Contents/Resources/bin
</pre>

3) Clone this repo:
<pre>
 > git clone https://github.com/cyrush/visit_pyopencl_exprs.git
</pre>

4) Use VisIt to install the required python support modules.

Note: You may have to load modules or set env vars to access the OpenCL headers and libs on your system.
To use the NVIDIA OpenCL platform, you will need to load the proper CUDA environment. The shell scripts in 
the _setup_scripts_ directory provide working examples for a few clusters. 
<pre>
 > visit -nowin -cli -s setup_scripts/install_visit_pyopencl_support.py
</pre>
5) Run module tests for flow & visit_flow_vpe
<pre>
 > ./run_tests.sh
</pre>


Getting Started with Flow Only (w/o) VisIt
-------------------------------------------
If you would like to run outside of VisIt, the setup script should work with a standalone python as well. 
<pre>
 > python setup_scripts/install_visit_pyopencl_support.py
</pre>

<pre>
 > cd flow
 > python setup.py test
</pre>



Getting Started On Edge (LLNL Visualization Cluster)
---------------
1) Clone this repo:
<pre>
 > git clone git://github.com/cyrush/visit_pyopencl_exprs.git
</pre>

2) Install necessary support python modules
<pre>
 > ./setup_scripts/edge_gcc_setup.sh
</pre>

3) Run tests in an mxterm (to access GPUS)
<pre>
 > mxterm 1 12 30
 [mxterm]> source setup_scripts/edge_gcc_env_vars.sh
 [mxterm]> ./run_tests.sh
</pre>



