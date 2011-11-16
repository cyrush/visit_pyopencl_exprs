VisIt pyopencl Expressions Sandbox
================================

This repo will be used to develop support for OpenCL based VisIt expressions.
For initial exploration and prototyping, we will bootstrap OpenCL into VisIt
via pyopencl and VisIt's Python Expression capability.

To get started:

* Install VisIt 2.4.0 or setup a development build of the VisIt trunk.
* Add `visit' to your path (bash example):
<pre>
 > export PATH=$PATH:/path/to/visit/bin
</pre>
* Clone this repo:
<pre>
 > git clone https://github.com/cyrush/visit_pyopencl_exprs.git
</pre>
* Install necessary support python modules into VisIt
<pre>
 > visit -nowin -cli -s install_visit_pyopencl_support.py
</pre>
* Run the module tests
<pre>
 > visit -nowin -cli -s setup.py test
</pre>
 
