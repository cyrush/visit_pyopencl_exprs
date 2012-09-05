#
# ${disclaimer}
#
"""
 file: pyocl_batch.py
 author: Cyrus Harrison <cyrush@llnl.gov>

 created: 9/1/2012
 description:
    Provides flow filters that execute PyOpenCLBatch operations.

"""
import logging
#logging.basicConfig(level=logging.INFO)
logging.basicConfig(level=logging.ERROR)


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
    log.info(msg,"filters.pyocl_batch")

def err(msg):
    log.error(msg,"filters.pyocl_batch")


class PyOpenCLBatchContext(Context):
    context_type = "pyocl_batch"
    def start(self,dev_id = 0):
        pyocl_env.Manager.set_device_id(dev_id)
        pyocl_env.Manager.clear_events()
        pyocl_env.Pool.reset()
    def set_device_id(self,dev_id):
        pyocl_env.Manager.set_device_id(dev_id)
    def set_output_shape(self,shape):
        self.out_shape = shape
    def execute_kernel(self,kernel_source,inputs,out_dim=None):
        buffers = []
        buffers.extend(inputs)
        vshape = self.__find_valid_shape(inputs)
        if out_dim is None:
            out_shape = vshape
        else:
            if out_dim == 1:
                out_shape = (vshape[0],)
            else:
                out_shape = (vshape[0],out_dim)
        msg  = "Execute Kernel:\n"
        msg += kernel_source
        info(msg)
        info("Execute Kernel: out_shape = " + str(out_shape))
        dest_buf = pyocl_env.Pool.request_buffer(out_shape,npy.float32)
        buffers.append(dest_buf)
        evnt = pyocl_env.Manager.dispatch_kernel(kernel_source,
                                                 out_shape,
                                                 buffers)
        return dest_buf
    def events_summary(self):
        return pyocl_env.Manager.events_summary()
    def __find_valid_shape(self,inputs):
        for ipt in inputs:
            return ipt.out_shape
        return self.out_shape

class PyOpenCLBatchSource(Filter):
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
        buf = pyocl_env.Pool.request_buffer(data.shape,data.dtype)
        buf.write(data)
        return buf


class PyOpenCLBatchAdd(Filter):
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

class PyOpenCLBatchSub(Filter):
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

class PyOpenCLBatchMult(Filter):
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

class PyOpenCLBatchDiv(Filter):
    filter_type    = "div"
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
              c[gid] = a[gid] / b[gid];
            }
            """
        return self.context.execute_kernel(kernel_source,inputs)

class PyOpenCLBatchMod(Filter):
    filter_type    = "mod"
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
              c[gid] = a[gid] % b[gid];
            }
            """
        return self.context.execute_kernel(kernel_source,inputs)

class PyOpenCLBatchCos(Filter):
    filter_type    = "cos"
    input_ports    = ["in"]
    default_params = {}
    output_port    = True
    def execute(self):
        inputs = [self.input("in")]
        kernel_source =  """
            __kernel void kmain(__global const float *a,
                                __global float *c)
            {
              int gid = get_global_id(0);
              c[gid] = cos(a[gid]);
            }
            """
        return self.context.execute_kernel(kernel_source,inputs)

class PyOpenCLBatchSin(Filter):
    filter_type    = "sin"
    input_ports    = ["in"]
    default_params = {}
    output_port    = True
    def execute(self):
        inputs = [self.input("in")]
        kernel_source =  """
            __kernel void kmain(__global const float *a,
                                __global float *c)
            {
              int gid = get_global_id(0);
              c[gid] = sin(a[gid]);
            }
            """
        return self.context.execute_kernel(kernel_source,inputs)

class PyOpenCLBatchTan(Filter):
    filter_type    = "tan"
    input_ports    = ["in"]
    default_params = {}
    output_port    = True
    def execute(self):
        inputs = [self.input("in")]
        kernel_source =  """
            __kernel void kmain(__global const float *a,
                                __global float *c)
            {
              int gid = get_global_id(0);
              c[gid] = tan(a[gid]);
            }
            """
        return self.context.execute_kernel(kernel_source,inputs)

class PyOpenCLBatchCeil(Filter):
    filter_type    = "ceil"
    input_ports    = ["in"]
    default_params = {}
    output_port    = True
    def execute(self):
        inputs = [self.input("in")]
        kernel_source =  """
            __kernel void kmain(__global const float *a,
                                __global float *c)
            {
              int gid = get_global_id(0);
              c[gid] = ceil(a[gid]);
            }
            """
        return self.context.execute_kernel(kernel_source,inputs)

class PyOpenCLBatchFloor(Filter):
    filter_type    = "floor"
    input_ports    = ["in"]
    default_params = {}
    output_port    = True
    def execute(self):
        inputs = [self.input("in")]
        kernel_source =  """
            __kernel void kmain(__global const float *a,
                                __global float *c)
            {
              int gid = get_global_id(0);
              c[gid] = floor(a[gid]);
            }
            """
        return self.context.execute_kernel(kernel_source,inputs)

class PyOpenCLBatchAbs(Filter):
    filter_type    = "abs"
    input_ports    = ["in"]
    default_params = {}
    output_port    = True
    def execute(self):
        inputs = [self.input("in")]
        kernel_source =  """
            __kernel void kmain(__global const float *a,
                                __global float *c)
            {
              int gid = get_global_id(0);
              c[gid] = abs(a[gid]);
            }
            """
        return self.context.execute_kernel(kernel_source,inputs)

class PyOpenCLBatchLog10(Filter):
    filter_type    = "log10"
    input_ports    = ["in"]
    default_params = {}
    output_port    = True
    def execute(self):
        inputs = [self.input("in")]
        kernel_source =  """
            __kernel void kmain(__global const float *a,
                                __global float *c)
            {
              int gid = get_global_id(0);
              c[gid] = log10(a[gid]);
            }
            """
        return self.context.execute_kernel(kernel_source,inputs)

class PyOpenCLBatchLog(Filter):
    filter_type    = "log"
    input_ports    = ["in"]
    default_params = {}
    output_port    = True
    def execute(self):
        inputs = [self.input("in")]
        kernel_source =  """
            __kernel void kmain(__global const float *a,
                                __global float *c)
            {
              int gid = get_global_id(0);
              c[gid] = log(a[gid]);
            }
            """
        return self.context.execute_kernel(kernel_source,inputs)

class PyOpenCLBatchExp(Filter):
    filter_type    = "exp"
    input_ports    = ["in"]
    default_params = {}
    output_port    = True
    def execute(self):
        inputs = [self.input("in")]
        kernel_source =  """
            __kernel void kmain(__global const float *a,
                                __global float *c)
            {
              int gid = get_global_id(0);
              c[gid] = exp(a[gid]);
            }
            """
        return self.context.execute_kernel(kernel_source,inputs)

class PyOpenCLBatchPow(Filter):
    filter_type    = "pow"
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
              c[gid] = pow(a[gid], b[gid]);
            }
            """
        return self.context.execute_kernel(kernel_source,inputs)

class PyOpenCLBatchId(Filter):
    filter_type    = "id"
    input_ports    = ["in"]
    default_params = {}
    output_port    = True
    def execute(self):
        inputs = [self.input("in")]
        kernel_source =  """
            __kernel void kmain(__global const float *a,
                                __global float *c)
            {
              int gid = get_global_id(0);
              c[gid] = a[gid];
            }
            """
        return self.context.execute_kernel(kernel_source,inputs)

class PyOpenCLBatchRound(Filter):
    filter_type    = "round"
    input_ports    = ["in"]
    default_params = {}
    output_port    = True
    def execute(self):
        inputs = [self.input("in")]
        kernel_source =  """
            __kernel void kmain(__global const float *a,
                                __global float *c)
            {
              int gid = get_global_id(0);
              int val = a[gid];
              if (val < 0.)
                c[gid] = - floor(fabs(val) + 0.5);
              else
                c[gid] = floor(fabs(val + 0.5));
            }
            """
        return self.context.execute_kernel(kernel_source,inputs)

class PyOpenCLBatchSquare(Filter):
    filter_type    = "square"
    input_ports    = ["in"]
    default_params = {}
    output_port    = True
    def execute(self):
        inputs = [self.input("in")]
        kernel_source =  """
            __kernel void kmain(__global const float *a,
                                __global float *c)
            {
              int gid = get_global_id(0);
              c[gid] = a[gid] * a[gid];
            }
            """
        return self.context.execute_kernel(kernel_source,inputs)

class PyOpenCLBatchSqrt(Filter):
    filter_type    = "sqrt"
    input_ports    = ["in"]
    default_params = {}
    output_port    = True
    def execute(self):
        inputs = [self.input("in")]
        kernel_source =  """
            __kernel void kmain(__global const float *a,
                                __global float *c)
            {
              int gid = get_global_id(0);
              c[gid] = sqrt(a[gid]);
            }
            """
        return self.context.execute_kernel(kernel_source,inputs)

class PyOpenCLBatchArrayCompose(Filter):
    filter_type    = "compose"
    input_ports    = ["in_a","in_b"]
    default_params = {}
    output_port    = True
    def execute(self):
        a = self.input("in_a")
        b = self.input("in_b")
        if len(a.shape) == 1:
            a = a.reshape(a.shape[0],1)
        if len(b.shape) == 1:
            b = b.reshape(a.shape[0],1)
        res = npy.hstack((a,b))
        return res

class PyOpenCLBatchArrayDecompose(Filter):
    filter_type    = "decompose"
    input_ports    = ["in"]
    default_params = {"index":0}
    output_port    = True
    def execute(self):
        p = self.params
        a = self.input("in")
        inputs = [a]
        dim = a.shape[1]
        idx = p.index
        kernel_source =  """
            __kernel void kmain(__global const float *v,
                                __global float *o)
            {
              int gid = get_global_id(0);
              o[gid] =  v[gid*%d+%d];
            }
            """ % (dim,idx)
        return self.context.execute_kernel(kernel_source,inputs,1)


class PyOpenCLBatchConst(Filter):
    filter_type    = "const"
    default_params = {"value":0.0}
    input_ports    = []
    output_port    = True
    def execute(self):
        p = self.params
        kernel_source =  """
            __kernel void kmain(__global float *o)
            {
              o[get_global_id(0)] =  %s;
            }
            """ % str(p.value)
        return self.context.execute_kernel(kernel_source,[])

class PyOpenCLBatchGrad2D(Filter):
    filter_type    = "grad2d"
    input_ports    = ["in", "dims", "x", "y"]
    default_params = {}
    output_port    = True
    def execute(self):
        inputs = [self.input("in"),
                  self.input("dims"),
                  self.input("x"),
                  self.input("y")
                  ]
        kernel_source =  """
            __kernel void kmain(__global const float *v,
                                __global const int   *d,
                                __global const float *x,
                                __global const float *y,
                                __global float *o)
            {
              int gid = get_global_id(0);
              int di = d[0]-1;
              int dj = d[1]-1;

              int zi = gid % di;
              int zj = gid / di;

              // for rectilinear, we only need 2 points to get dx,dy
              int pi0 = zi + zj*(di+1);
              int pi1 = zi + 1 + (zj+1)*(di+1);

              float vv = v[gid];

              float vx0 = vv;
              float vx1 = vv;
              if(zi > 0)    vx0 = v[gid-1];
              if(zi < di-1) vx1 = v[gid+1];

              float vy0 = vv;
              float vy1 = vv;
              if(zj > 0)    vy0 = v[zi + (zj-1)*di];
              if(zj < dj-1) vy1 = v[zi + (zj+1)*di];

              float x0 = x[pi0];
              float x1 = x[pi1];

              float y0 = y[pi0];
              float y1 = y[pi1];

              float dx = (x1 - x0);
              float dy = (y1 - y0);
              float dvdx = .5  * (vx1 - vx0) / dx;
              float dvdy = .5  * (vy1 - vy0) / dy;

              // forward diff @ boundries
              if(zi == 0)    dvdx = (vx1 - vx0)/dx;
              if(zi == di-1) dvdx = (vx1 - vx0)/dx;
              if(zj == 0)    dvdy = (vy1 - vy0)/dy;
              if(zj == dj-1) dvdy = (vy1 - vy0)/dy;

              o[gid*3]   = dvdx;
              o[gid*3+1] = dvdy;
            }
            """
        return self.context.execute_kernel(kernel_source,inputs,out_dims=2)

class PyOpenCLBatchGrad3D(Filter):
    filter_type    = "grad"
    input_ports    = ["dims","x","y","z","in"]
    default_params = {}
    output_port    = True
    def execute(self):
        inputs = [self.input("in"),
                  self.input("dims"),
                  self.input("x"),
                  self.input("y"),
                  self.input("z")]
        kernel_source =  """
            __kernel void kmain(__global const float *v,
                                __global const int   *d,
                                __global const float *x,
                                __global const float *y,
                                __global const float *z,
                                __global float *o)
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

                o[gid*3]   = df.x;
                o[gid*3+1] = df.y;
                o[gid*3+2] = df.z;
            }
            """
        return self.context.execute_kernel(kernel_source,inputs,out_dim=3)

class PyOpenCLBatchCurl2D(Filter):
    filter_type    = "curl2d"
    input_ports    = ["in_dfx", "in_dfy"]
    default_params = {}
    output_port    = True
    def execute(self):
        inputs = [self.input("in_dfx"),
                  self.input("in_dfy")]
        kernel_source =  """
            __kernel void kmain(__global const float *dfx,
                                __global const float *dfy,
                                __global float *o)
            {
              int gid = get_global_id(0);
              float dfxdy = dfx[gid*3+2];
              float dfydx = dfy[gid*3];
              o[gid] = dfydx - dfxdy;
            }
            """
        return self.context.execute_kernel(kernel_source,inputs)

class PyOpenCLBatchCurl3D(Filter):
    filter_type    = "curl3d"
    input_ports    = ["in_dfx", "in_dfy", "in_dfz"]
    default_params = {}
    output_port    = True
    def execute(self):
        inputs = [self.input("in_dfx"),
                  self.input("in_dfy"),
                  self.input("in_dfz"),]
        kernel_source =  """
            __kernel void kmain(__global const float *dfx,
                                __global const float *dfy,
                                __global const float *dfz,
                                __global float *o)
            {
              int gid = get_global_id(0);

              float dfzdy = dfz[gid*3+1];
              float dfydz = dfy[gid*3+2];

              float dfxdz = dfx[gid*3+2];
              float dfzdx = dfz[gid*3];

              float dfydx = dfy[gid*3];
              float dfxdy = dfx[gid*3+1];

              o[gid*3]   = dfzdy - dfydz;
              o[gid*3+1] = dfxdz - dfzdx;
              o[gid*3+2] = dfydx - dfxdy;
            }
            """
        return self.context.execute_kernel(kernel_source,inputs,out_dim=3)

filters = [PyOpenCLBatchSource,
           PyOpenCLBatchAdd,
           PyOpenCLBatchSub,
           PyOpenCLBatchMult,
           PyOpenCLBatchDiv,
           PyOpenCLBatchMod,
           PyOpenCLBatchCos,
           PyOpenCLBatchSin,
           PyOpenCLBatchTan,
           PyOpenCLBatchCeil,
           PyOpenCLBatchFloor,
           PyOpenCLBatchAbs,
           PyOpenCLBatchLog10,
           PyOpenCLBatchLog,
           PyOpenCLBatchExp,
           PyOpenCLBatchPow,
           PyOpenCLBatchId,
           PyOpenCLBatchRound,
           PyOpenCLBatchSquare,
           PyOpenCLBatchSqrt,
           PyOpenCLBatchArrayCompose,
           PyOpenCLBatchArrayDecompose,
           PyOpenCLBatchConst,
           PyOpenCLBatchGrad2D,
           PyOpenCLBatchGrad3D,
           PyOpenCLBatchCurl2D,
           PyOpenCLBatchCurl3D]

contexts = [PyOpenCLBatchContext]

