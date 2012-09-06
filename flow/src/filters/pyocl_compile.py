#
# ${disclaimer}
#
"""
 file: pyocl_compile.py
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
import pyocl_env

def info(msg):
    log.info(msg,"filters.pyocl_compile")

class PyOpenCLCompileContext(Context):
    context_type = "pyocl_compile"
    def start(self,platform_id, device_id):
        pyocl_env.Manager.select_device(platform_id,device_id)
        pyocl_env.Manager.clear_events()
        pyocl_env.Pool.reset()
        self.kernels = {}
        self.stmts   = []
        self.inputs  = []
        self.out_shape = None
    def set_device_id(self,dev_id):
        pyocl_env.Manager.set_device_id(dev_id)
    def bind_data(self,obj):
        idx = len(self.inputs)
        self.inputs.append(obj)
        base = "in_%04d" %idx
        return ("%s_fetch" % base, base)
    def set_output_shape(self,shape):
        self.out_shape = shape
    def add_decompose(self,var,out_type = "float"):
        idx = len(self.stmts)
        res_name  = "_auto_res_%04d" % idx
        stmt = "%s %s = %s;" % (out_type,res_name,var)
        self.stmts.append(stmt)
        return (res_name,None)
    def add_call(self,kernel_name,
                      kernel_source,
                      args,
                      in_types = None,
                      out_type = "float"):
        idx = len(self.stmts)
        if not kernel_name in self.kernels.keys():
            self.kernels[kernel_name] = kernel_source
        res_name  = "_auto_res_%04d" % idx
        stmt = "%s(" % kernel_name
        if in_types is None:
            in_types = ["fetch"]*len(args)
        for idx in range(len(args)):
            arg = args[idx]
            if in_types[idx] == "fetch":
                stmt += "%s," % arg[0]
            else:
                stmt += "%s," % arg[1]
        stmt = stmt[:-1] + ")"
        stmt = "%s %s = %s;" % (out_type,res_name,stmt)
        self.stmts.append(stmt)
        return (res_name,None)
    def compile(self):
        act = pyocl_env.PyOpenCLHostTimer("auto_kgen",0)
        act.start()
        res = ""
        for kern in self.kernels.values():
            res += kern
        ident = "            "
        args_ident = "                               "
        res += "\n%s__kernel void kmain(" % ident
        for idx in range(len(self.inputs)):
            if self.inputs[idx].dtype == npy.int32:
                itype = "int  "
            else:
                itype = "float"
            iname = "in_%04d" % idx
            res  += "__global const %s *%s,\n%s " % (itype,iname,args_ident)
        res += " __global float *out)\n"
        res += "%s{\n" % ident
        res += "%s int gid = get_global_id(0);\n" % ident
        for idx in range(len(self.inputs)):
            if self.inputs[idx].dtype == npy.int32:
                itype = "int  "
            else:
                itype = "float"
            iname = "in_%04d" % idx
            res += "%s %s %s_fetch = %s[gid];\n" % (ident,itype,iname,iname)
        for stmt in self.stmts:
            res += "%s %s\n" % (ident,stmt)
        res += "%s out[gid] = _auto_res_%04d;\n" % (ident,len(self.stmts)-1)
        res += "%s}\n" % ident
        act.stop()
        pyocl_env.Manager.add_host_event(act)
        return res
    def run(self):
        # run in context
        kernel_source = self.compile()
        return self.execute_kernel(kernel_source,self.inputs)
    def execute_kernel(self,kernel_source,inputs):
        msg  = "Execute Kernel:\n"
        msg += kernel_source
        info(msg)
        buffers = []
        for ipt in inputs:
            buf = pyocl_env.Pool.request_buffer(ipt.shape,ipt.dtype)
            buf.write(ipt)
            buffers.append(buf)
        dest_buf = pyocl_env.Pool.request_buffer(self.out_shape,npy.float32)
        buffers.append(dest_buf)
        pyocl_env.Manager.dispatch_kernel(kernel_source,
                                          self.out_shape,
                                          buffers)
        return dest_buf.read()
    def events_summary(self):
        return pyocl_env.Manager.events_summary()

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

class PyOpenCLCompileArrayDecompose(Filter):
    filter_type    = "decompose"
    input_ports    = ["in"]
    default_params = {"index":0}
    output_port    = True
    def execute(self):
        p = self.params
        a = self.input("in")
        res = ("%s.s%d" % (a[0],p.index), None)
        self.context.add_decompose(res[0])
        return ("%s.s%d" % (a[0],p.index), None)


class PyOpenCLCompileConst(Filter):
    filter_type    = "const"
    default_params = {"value":0}
    input_ports    = []
    output_port    = True
    def execute(self):
        p = self.params
        return ("%s" % str(p.value), None)


class PyOpenCLCompileGrad3D(Filter):
    filter_type    = "grad"
    input_ports    = ["dims","x","y","z","in"]
    default_params = {}
    output_port    = True
    def execute(self):
        args = [self.input("in"),
                self.input("dims"),
                self.input("x"),
                self.input("y"),
                self.input("z")]
        kernel_source =  """
            float4 kgrad3d(__global const float *v,
                           __global const int   *d,
                           __global const float *x,
                           __global const float *y,
                           __global const float *z)
            {
                int gid = get_global_id(0);

                int di = d[0]-1;
                int dj = d[1]-1;
                int dk = d[2]-1;

                int zi = gid % di;
                int zj = (gid / di) % dj;
                int zk = (gid / di) / dj;

                // for rectilinear, we only need 2 points to get dx,dy,dz
                int pi0 = zi + zj*(di+1) + zk*(di+1)*(dj+1);
                int pi1 = zi + 1 + (zj+1)*(di+1) + (zk+1)*(di+1)*(dj+1);

                float vv = v[gid];
                float4 p_0 = (float4)(x[pi0],y[pi0],z[pi0],1.0);
                float4 p_1 = (float4)(x[pi1],y[pi1],z[pi1],1.0);
                float4 dg  = p_1 - p_0;

                // value
                float4 f_0 = (float4)(vv,vv,vv,1.0);
                float4 f_1 = (float4)(vv,vv,vv,1.0);

                // i bounds
                if(zi > 0)
                {
                    f_0.x = v[gid-1];
                }

                if(zi < (di-1))
                {
                    f_1.x = v[gid+1];
                }

                // j bounds
                if(zj > 0)
                {
                    f_0.y = v[gid-di];
                }

                if(zj < (dj-1))
                {
                    f_1.y = v[gid+di];
                }

                // k bounds
                if(zk > 0)
                {
                    f_0.z = v[gid-(di*dj)];
                }

                if(zk < (dk-1))
                {
                    f_1.z = v[gid+(di*dj)];
                }

                float4 df = (f_1 - f_0) / dg;

                // central diff if we aren't on the edges
                if( (zi != 0) && (zi != (di-1)))
                {
                    df.x *= .5;
                }

                // central diff if we aren't on the edges
                if( (zj != 0) && (zj != (dj-1)))
                {
                    df.y *= .5;
                }

                // central diff if we aren't on the edges
                if( (zk != 0) && (zk != (dk-1)))
                {
                    df.z *= .5;
                }
                //return (float4)(1.0,2.0,3.0,0.0);
                return df;
            }
            """
        return self.context.add_call("kgrad3d",
                                     kernel_source,
                                     args,
                                     in_types = ["direct",
                                                 "direct",
                                                 "direct",
                                                 "direct",
                                                 "direct"],
                                     out_type = "float4")

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
           PyOpenCLCompileSqrt,
           PyOpenCLCompileArrayDecompose,
           PyOpenCLCompileGrad3D,
           PyOpenCLCompileConst]

contexts = [PyOpenCLCompileContext]
