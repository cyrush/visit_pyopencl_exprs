#
# ${disclaimer}
#
"""
 file: pyopenclf_ops.py
 author: Maysam Moussalem <maysam@tacc.utexas.edu>
 created: 04/04/2012
 description:
    Provides flow filters that execute built-in PyOpenCL operations.

"""

# Guarded import of pyopencl
found_pyopencl = False
try:
    import numpy as npy
    import pyopencl as cl
    import pyopencl.array as cla
    import pyopencl.clmath as clm
    found_pyopencl = True
except ImportError:
    pass

from ..core import Filter, Context, log

def info(msg):
    log.info(msg,"filters.pyoclf_ops")

class PyOpenCLContext(Context):
    context_type = "pyoclf_ops"
    def start(self):
        """ Execute PyOpenCL function to calc: out = a+b. """
        self.ctx = cl.create_some_context()
        self.queue = cl.CommandQueue(self.ctx, properties=cl.command_queue_properties.PROFILING_ENABLE)
    def create_memory(self):
        """ Send input to device. """
        for ipt in inputs:
            cla.to_device(self.queue, ipt)

class PyOpenCLFAdd(Filter):
    filter_type    = "add"
    input_ports    = ["in_a","in_b"]
    default_params = {}
    output_port    = True
    def execute(self):
        inputs = [self.input("in_a"), self.input("in_b")]
        return self.input("in_a").__add__(self.input("in_b"))

class PyOpenCLFSub(Filter):
    filter_type    = "sub"
    input_ports    = ["in_a","in_b"]
    default_params = {}
    output_port    = True
    def execute(self):
        inputs = [self.input("in_a"), self.input("in_b")]
        return self.input("in_a").__sub__(self.input("in_b"))

class PyOpenCLFMult(Filter):
    filter_type    = "mult"
    input_ports    = ["in_a","in_b"]
    default_params = {}
    output_port    = True
    def execute(self):
        inputs = [self.input("in_a"), self.input("in_b")]
        return self.input("in_a").__mul__(self.input("in_b"))

class PyOpenCLFDiv(Filter):
    filter_type    = "div"
    input_ports    = ["in_a","in_b"]
    default_params = {}
    output_port    = True
    def execute(self):
        inputs = [self.input("in_a"), self.input("in_b")]
        return self.input("in_a").__div__(self.input("in_b"))

class PyOpenCLFCos(Filter):
    filter_type    = "cos"
    input_ports    = ["in"]
    default_params = {}
    output_port    = True
    def execute(self):
        inputs = [self.input("in")]
        return clm.cos(self.input("in"))

class PyOpenCLFSin(Filter):
    filter_type    = "sin"
    input_ports    = ["in"]
    default_params = {}
    output_port    = True
    def execute(self):
        inputs = [self.input("in")]
        return clm.sin(self.input("in"))

filters = [PyOpenCLFAdd,
           PyOpenCLFSub,
           PyOpenCLFMult,
           PyOpenCLFDiv,
           PyOpenCLFCos,
           PyOpenCLFSin]

contexts = [PyOpenCLContext]
