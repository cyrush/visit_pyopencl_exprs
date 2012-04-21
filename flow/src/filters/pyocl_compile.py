#
# ${disclaimer}
#
"""
 file: npy_ops.py
 author: Cyrus Harrison <cyrush@llnl.gov>
 created: 3/24/2012
 description:
    Provides flow filters that compile and execute numpy operations.

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
import pyocl_context

def info(msg):
    log.info(msg,"filters.pyocl_compile")

class PyOpenCLCompileContext(Context):
    context_type = "pyocl_compile"
    def start(self):
        self.kernels = {}
        self.stmts   = []
        self.inputs  = []
    def bind_data(self,obj):
        idx = len(self.inputs)
        self.inputs.append(obj)
        return "in_%04d[gid]" % idx
    def add_call(self,kernel_name,kernel_source,args):
        idx = len(self.stmts)
        if not kernel_name in self.kernels.keys():
            self.kernels[kernel_name] = kernel_source
        res_name  = "_auto_res_%04d" % idx
        stmt = "%s(" % kernel_name
        for arg in args:
            stmt += "%s," % arg
        stmt = stmt[:-1] + ")"
        stmt = "float %s = %s;" % (res_name,stmt)
        self.stmts.append(stmt)
        return res_name
    def compile(self):
        res = ""
        for kern in self.kernels.values():
            res += kern
        ident = "            "
        args_ident = "                               "
        res += "\n%s__kernel void kmain(" % ident
        for idx in range(len(self.inputs)):
            iname = "in_%04d" % idx
            res  += "__global const float *%s,\n%s" % (iname,args_ident)
        res += "__global float *out)\n"
        res += "%s{\n" % ident
        res += "%s int gid = get_global_id(0);\n" % ident
        for stmt in self.stmts:
            res += "%s %s\n" % (ident,stmt)
        res += "%s out[gid] = _auto_res_%04d;\n" % (ident,len(self.stmts)-1)
        res += "%s}\n" % ident
        return res
    def run(self):
        # run in context
        kernel_source = self.compile()
        return self.execute_kernel(kernel_source,self.inputs)
    def execute_kernel(self,kernel_source,inputs):
        ctx = pyocl_context.instance()
        msg  = "Execute Kernel:\n"
        msg += kernel_source
        info(msg)
        queue = cl.CommandQueue(ctx)
        mf    = cl.mem_flags
        buffers = []
        for ipt in inputs:
            buf = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=ipt)
            buffers.append(buf)
        res = npy.zeros(inputs[0].shape,dtype=npy.float32)
        dest_buf = cl.Buffer(ctx, mf.WRITE_ONLY, res.nbytes)
        buffers.append(dest_buf)
        prg = cl.Program(ctx,kernel_source).build()
        prg.kmain(queue, res.shape, None, *buffers)
        cl.enqueue_copy(queue, res, dest_buf)
        return res


class PyOpenCLCompileSource(Filter):
    # overrides standard RegistrySource
    filter_type    = "<registry_source>"
    input_ports    = []
    default_params = {}
    output_port    = True
    def execute(self):
        # fetch data from registry 
        # the instance name determines the reg entry_key
        key  = self.name[self.name.rfind(":"):]
        data = self.context.registry_fetch(key)
        # bind var into the context
        var_name = self.context.bind_data(data)
        return var_name


class PyOpenCLCompileAdd(Filter):
    filter_type    = "add"
    input_ports    = ["in_a","in_b"]
    default_params = {}
    output_port    = True
    def execute(self):
        args = [self.input("in_a"), self.input("in_b")]
        kernel_source =  """
            float kadd(const float a,const float b)
            {return a + b;}
            """
        return self.context.add_call("kadd",kernel_source,args)

class PyOpenCLCompileSub(Filter):
    filter_type    = "sub"
    input_ports    = ["in_a","in_b"]
    default_params = {}
    output_port    = True
    def execute(self):
        args = [self.input("in_a"), self.input("in_b")]
        kernel_source =  """
            float ksub(const float a,const float b)
            {return a - b;}
            """
        return self.context.add_call("ksub",kernel_source,args)

class PyOpenCLCompileMult(Filter):
    filter_type    = "mult"
    input_ports    = ["in_a","in_b"]
    default_params = {}
    output_port    = True
    def execute(self):
        args = [self.input("in_a"), self.input("in_b")]
        kernel_source =  """
            float kmult(const float a,const float b)
            {return a * b;}
            """
        return self.context.add_call("kmult",kernel_source,args)

filters = [PyOpenCLCompileSource,
           PyOpenCLCompileAdd,
           PyOpenCLCompileSub,
           PyOpenCLCompileMult]

contexts = [PyOpenCLCompileContext]
