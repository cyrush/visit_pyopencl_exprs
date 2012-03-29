#
# ${disclaimer}
#
"""
 file: npy_ops.py
 author: Cyrus Harrison <cyrush@llnl.gov>
 created: 3/24/2012
 description:
    Provides flow filters that execute pyopencl operations.

"""

# Guarded import of pyopencl
found_pyopencl = False
try:
    import numpy as npy
    import pyopencl as cl
    found_pyopencl = True
except ImportError:
    pass

from ..core import Filter, Context, log

def info(msg):
    log.info(msg,"filters.pyocl_ops")

class PyOpenCLContext(Context):
    context_type = "pyocl_ops"
    def start(self):
        """ Execute OpenCL kernel to calc: out = a+b. """
        self.ctx = cl.create_some_context()
    def execute_kernel(self,kernel_source,inputs):
        msg  = "Execute Kernel:\n"
        msg += kernel_source
        info(msg)
        queue = cl.CommandQueue(self.ctx)
        mf    = cl.mem_flags
        buffers = []
        for ipt in inputs:
            buf = cl.Buffer(self.ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=ipt)
            buffers.append(buf)
        res = npy.zeros(inputs[0].shape,dtype=npy.float32)
        dest_buf = cl.Buffer(self.ctx, mf.WRITE_ONLY, res.nbytes)
        buffers.append(dest_buf)
        prg = cl.Program(self.ctx,kernel_source).build()
        prg.kmain(queue, res.shape, None, *buffers)
        cl.enqueue_copy(queue, res, dest_buf)
        return res

class PyOpenCLAdd(Filter):
    filter_type    = "add"
    input_ports    = ["in_a","in_b"]
    default_params = {}
    output_port    = True
    def execute(self):
        inputs = [self.input("in_a"), self.input("in_b")]
        kernel_source =  """
            __kernel void kmain(__global const float *a,
                                __global const float *b,
                                __global float *c)
            {
              int gid = get_global_id(0);
              c[gid] = a[gid] + b[gid];
            }
            """
        return self.context.execute_kernel(kernel_source,inputs)

class PyOpenCLSub(Filter):
    filter_type    = "sub"
    input_ports    = ["in_a","in_b"]
    default_params = {}
    output_port    = True
    def execute(self):
        inputs = [self.input("in_a"), self.input("in_b")]
        kernel_source =  """
            __kernel void kmain(__global const float *a,
                                __global const float *b,
                                __global float *c)
            {
              int gid = get_global_id(0);
              c[gid] = a[gid] - b[gid];
            }
            """
        return self.context.execute_kernel(kernel_source,inputs)

class PyOpenCLMult(Filter):
    filter_type    = "mult"
    input_ports    = ["in_a","in_b"]
    default_params = {}
    output_port    = True
    def execute(self):
        inputs = [self.input("in_a"), self.input("in_b")]
        kernel_source =  """
            __kernel void kmain(__global const float *a,
                                __global const float *b,
                                __global float *c)
            {
              int gid = get_global_id(0);
              c[gid] = a[gid] * b[gid];
            }
            """
        return self.context.execute_kernel(kernel_source,inputs)

filters = [PyOpenCLAdd,
           PyOpenCLSub,
           PyOpenCLMult]

contexts = [PyOpenCLContext]
