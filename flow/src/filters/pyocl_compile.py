#
# ${disclaimer}
#
"""
 file: npy_ops.py
 author: Cyrus Harrison <cyrush@llnl.gov>
         Maysam Moussalem <maysam@cs.utexas.edu>
 created: 3/24/2012
 description:
    Provides flow filters that compile and execute PyOpenCL operations.

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
    log.info(msg,"filters.pyocl_compile")

class PyOpenCLCompileContext(Context):
    context_type = "pyocl_compile"
    def start(self):
        self.ctx = cl.create_some_context()
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
        msg  = "Execute Kernel:\n"
        msg += kernel_source
        info(msg)
        queue = cl.CommandQueue(self.ctx, properties=cl.command_queue_properties.PROFILING_ENABLE)
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

class PyOpenCLCompileDiv(Filter):
    filter_type    = "div"
    input_ports    = ["in_a","in_b"]
    default_params = {}
    output_port    = True
    def execute(self):
        args = [self.input("in_a"), self.input("in_b")]
        kernel_source =  """
            float kdiv(const float a,const float b)
            {return a / b;}
            """
        return self.context.add_call("kdiv",kernel_source,args)

class PyOpenCLCompileMod(Filter):
    filter_type    = "mod"
    input_ports    = ["in_a","in_b"]
    default_params = {}
    output_port    = True
    def execute(self):
        args = [self.input("in_a"), self.input("in_b")]
        kernel_source =  """
            float kmod(const float a, const float b)
            {return a % b;}
            """
        return self.context.add_call("kmod",kernel_source,args)

class PyOpenCLCompileCos(Filter):
    filter_type    = "cos"
    input_ports    = ["in"]
    default_params = {}
    output_port    = True
    def execute(self):
        args = [self.input("in")]
        kernel_source =  """
            float kcos(const float a)
            {return cos(a);}
            """
        return self.context.add_call("kcos",kernel_source,args)

class PyOpenCLCompileSin(Filter):
    filter_type    = "sin"
    input_ports    = ["in"]
    default_params = {}
    output_port    = True
    def execute(self):
        args = [self.input("in")]
        kernel_source =  """
            float ksin(const float a)
            {return sin(a);}
            """
        return self.context.add_call("ksin",kernel_source,args)

class PyOpenCLCompileTan(Filter):
    filter_type    = "tan"
    input_ports    = ["in"]
    default_params = {}
    output_port    = True
    def execute(self):
        args = [self.input("in")]
        kernel_source =  """
            float ktan(const float a)
            {return tan(a);}
            """
        return self.context.add_call("ktan",kernel_source,args)

class PyOpenCLCompileCeil(Filter):
    filter_type    = "ceil"
    input_ports    = ["in"]
    default_params = {}
    output_port    = True
    def execute(self):
        args = [self.input("in")]
        kernel_source =  """
            float kceil(const float a)
            {return ceil(a);}
            """
        return self.context.add_call("kceil",kernel_source,args)

class PyOpenCLCompileFloor(Filter):
    filter_type    = "floor"
    input_ports    = ["in"]
    default_params = {}
    output_port    = True
    def execute(self):
        args = [self.input("in")]
        kernel_source =  """
            float kfloor(const float a)
            {return floor(a);}
            """
        return self.context.add_call("kfloor",kernel_source,args)

class PyOpenCLCompileAbs(Filter):
    filter_type    = "abs"
    input_ports    = ["in"]
    default_params = {}
    output_port    = True
    def execute(self):
        args = [self.input("in")]
        kernel_source =  """
            float kabs(const float a)
            {return abs(a);}
            """
        return self.context.add_call("kabs",kernel_source,args)

class PyOpenCLCompileLog10(Filter):
    filter_type    = "log10"
    input_ports    = ["in"]
    default_params = {}
    output_port    = True
    def execute(self):
        args = [self.input("in")]
        kernel_source =  """
            float klog10(const float a)
            {return log10(a);}
            """
        return self.context.add_call("klog10",kernel_source,args)

class PyOpenCLCompileLog(Filter):
    filter_type    = "log"
    input_ports    = ["in"]
    default_params = {}
    output_port    = True
    def execute(self):
        args = [self.input("in")]
        kernel_source =  """
            float klog(const float a)
            {return log(a);}
            """
        return self.context.add_call("klog",kernel_source,args)

class PyOpenCLCompileExp(Filter):
    filter_type    = "exp"
    input_ports    = ["in"]
    default_params = {}
    output_port    = True
    def execute(self):
        args = [self.input("in")]
        kernel_source =  """
            float kexp(const float a)
            {return exp(a);}
            """
        return self.context.add_call("kexp",kernel_source,args)

class PyOpenCLCompilePow(Filter):
    filter_type    = "pow"
    input_ports    = ["in_a", "in_b"]
    default_params = {}
    output_port    = True
    def execute(self):
        args = [self.input("in_a"), self.input("in_b")]
        kernel_source =  """
            float kpow(const float a, const float b)
            {return kpow(a, b);}
            """
        return self.context.add_call("kpow",kernel_source,args)

class PyOpenCLCompileId(Filter):
    filter_type    = "id"
    input_ports    = ["in"]
    default_params = {}
    output_port    = True
    def execute(self):
        args = [self.input("in")]
        kernel_source =  """
            float kid(const float a)
            {return a;}
            """
        return self.context.add_call("kid",kernel_source,args)

class PyOpenCLCompileRound(Filter):
    filter_type    = "round"
    input_ports    = ["in"]
    default_params = {}
    output_port    = True
    def execute(self):
        args = [self.input("in")]
        kernel_source =  """
            float kround(const float a)
            {if (a < 0.) return (-floor(fabs(a) + 0.5));
             else return floor(fabs(a + 0.5))}
            """
        return self.context.add_call("kround",kernel_source,args)

class PyOpenCLCompileSquare(Filter):
    filter_type    = "square"
    input_ports    = ["in"]
    default_params = {}
    output_port    = True
    def execute(self):
        args = [self.input("in")]
        kernel_source =  """
            float ksquare(const float a)
            {return a*a;}
            """
        return self.context.add_call("ksquare",kernel_source,args)

class PyOpenCLCompileSqrt(Filter):
    filter_type    = "sqrt"
    input_ports    = ["in"]
    default_params = {}
    output_port    = True
    def execute(self):
        args = [self.input("in")]
        kernel_source =  """
            float ksqrt(const float a)
            {return sqrt(a);}
            """
        return self.context.add_call("ksqrt",kernel_source,args)

filters = [PyOpenCLCompileSource,
           PyOpenCLCompileAdd,
           PyOpenCLCompileSub,
           PyOpenCLCompileMult,
           PyOpenCLCompileDiv,
           PyOpenCLCompileMod,
           PyOpenCLCompileCos,
           PyOpenCLCompileSin,
           PyOpenCLCompileTan,
           PyOpenCLCompileCeil,
           PyOpenCLCompileFloor,
           PyOpenCLCompileAbs,
           PyOpenCLCompileLog10,
           PyOpenCLCompileLog,
           PyOpenCLCompileExp,
           PyOpenCLCompilePow,
           PyOpenCLCompileId,
           PyOpenCLCompileRound,
           PyOpenCLCompileSquare,
           PyOpenCLCompileSqrt]

contexts = [PyOpenCLCompileContext]
