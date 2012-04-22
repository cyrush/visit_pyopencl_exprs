#
# ${disclaimer}
#
"""
 file: pyocl_ops.py
 author: Cyrus Harrison <cyrush@llnl.gov>
         Maysam Moussalem <maysam@tacc.utexas.edu>
 created: 3/24/2012
 description:
    Provides flow filters that execute PyOpenCL operations.

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
    log.info(msg,"filters.pyocl_ops")

class PyOpenCLContext(Context):
    context_type = "pyocl_ops"
    def start(self):
        """ Start context"""
        pass
    def execute_kernel(self,kernel_source,inputs):
        ctx = pyocl_context.instance()
        msg  = "Execute Kernel:\n"
        msg += kernel_source
        info(msg)
        queue = cl.CommandQueue(ctx, properties=cl.command_queue_properties.PROFILING_ENABLE)
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

class PyOpenCLDiv(Filter):
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

class PyOpenCLMod(Filter):
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

class PyOpenCLCos(Filter):
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

class PyOpenCLSin(Filter):
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

class PyOpenCLTan(Filter):
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

class PyOpenCLCeil(Filter):
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

class PyOpenCLFloor(Filter):
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

class PyOpenCLAbs(Filter):
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

class PyOpenCLLog10(Filter):
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

class PyOpenCLLog(Filter):
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

class PyOpenCLExp(Filter):
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

class PyOpenCLPow(Filter):
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
              c[gid] = pow([gid], b[gid]);
            }
            """
        return self.context.execute_kernel(kernel_source,inputs)

class PyOpenCLId(Filter):
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

class PyOpenCLRound(Filter):
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

class PyOpenCLSquare(Filter):
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

class PyOpenCLSqrt(Filter):
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

class PyOpenCLGrad2D(Filter):
    filter_type    = "grad2d"
    input_ports    = ["in_d", "in_x", "in_y", "in_v", "in_o"]
    default_params = {}
    output_port    = True
    def execute(self):
        inputs = [self.input("in_d"), self.input("in_x"), self.input("in_y"),
                  self.input("in_v"), self.input("in_o")]
        kernel_source =  """
            __kernel void kmain(__global const int   *d,
                                __global const float *x,
                                __global const float *y,
                                __global const float *v, 
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
        return self.context.execute_kernel(kernel_source,inputs)

class PyOpenCLGrad3D(Filter):
    filter_type    = "grad3d"
    input_ports    = ["in"]
    default_params = {}
    output_port    = True
    def execute(self):
        inputs = [self.input("in_d"), self.input("in_x"), self.input("in_y"),
                  self.input("in_z"), self.input("in_v"), self.input("in_o")]
        kernel_source =  """
            __kernel void kmain(__global const int   *d,
                                __global const float *x,
                                __global const float *y,
                                __global const float *z,
                                __global const float *v, 
                                __global float *o)
            {
              int gid = get_global_id(0);
              int di = d[0]-1;
              int dj = d[1]-1;
              int dk = d[2]-1;

              int zi = gid % di;
              int zj = (gid / di) % dj;
              int zk =  (gid / di) / dj;

              // for rectilinear, we only need 2 points to get dx,dy,dz
              int pi0 = zi + zj*(di+1) + zk*(di+1)*(dj+1);
              int pi1 = zi + 1 + (zj+1)*(di+1) + (zk+1)*(di+1)*(dj+1);
  
              float vv = v[gid];

              float vx0 = vv;
              float vx1 = vv;
              if(zi > 0)    vx0 = v[gid-1];
              if(zi < di-1) vx1 = v[gid+1];

              float vy0 = vv;
              float vy1 = vv;
              if(zj > 0)    vy0 = v[zi + (zj-1)*di + zk*(di*dj)];
              if(zj < dj-1) vy1 = v[zi + (zj+1)*di + zk*(di*dj)];

              float vz0 = vv;
              float vz1 = vv;
              if(zk > 0)    vz0 = v[zi + zj*di + (zk-1)*(di*dj)];
              if(zk < dk-1) vz1 = v[zi + zj*di + (zk+1)*(di*dj)];

              float x0 = x[pi0];
              float x1 = x[pi1];

              float y0 = y[pi0];
              float y1 = y[pi1];

              float z0 = z[pi0];
              float z1 = z[pi1];

              float dx = (x1 - x0);
              float dy = (y1 - y0);
              float dz = (z1 - z0);
              float dvdx = .5  * (vx1 - vx0) / dx;
              float dvdy = .5  * (vy1 - vy0) / dy;
              float dvdz = .5  * (vz1 - vz0) / dz;

              // forward diff @ boundries
              if(zi == 0)    dvdx = (vx1 - vx0)/dx;
              if(zi == di-1) dvdx = (vx1 - vx0)/dx;
              if(zj == 0)    dvdy = (vy1 - vy0)/dy;
              if(zj == dj-1) dvdy = (vy1 - vy0)/dy;
              if(zk == 0)    dvdz = (vz1 - vz0)/dz;
              if(zk == dk-1) dvdz = (vz1 - vz0)/dz;

              o[gid*3]   = dvdx;
              o[gid*3+1] = dvdy;
              o[gid*3+2] = dvdz;

            }
            """
        return self.context.execute_kernel(kernel_source,inputs)

class PyOpenCLCurl2D(Filter):
    filter_type    = "curl2d"
    input_ports    = ["in_dfx", "in_dfy", "in_o"]
    default_params = {}
    output_port    = True
    def execute(self):
        inputs = [self.input("in_dfx"), self.input("in_dfy"),
                  self.input("in_o")]
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

class PyOpenCLCurl3D(Filter):
    filter_type    = "curl3d"
    input_ports    = ["in_dfx", "in_dfy", "in_dfz", "in_o"]
    default_params = {}
    output_port    = True
    def execute(self):
        inputs = [self.input("in_dfx"), self.input("in_dfy"),
                  self.input("in_dfz"), self.input("in_o")]
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
        return self.context.execute_kernel(kernel_source,inputs)

filters = [PyOpenCLAdd,
           PyOpenCLSub,
           PyOpenCLMult,
           PyOpenCLDiv,
           PyOpenCLMod,
           PyOpenCLCos,
           PyOpenCLSin,
           PyOpenCLTan,
           PyOpenCLCeil,
           PyOpenCLFloor,
           PyOpenCLAbs,
           PyOpenCLLog10,
           PyOpenCLLog,
           PyOpenCLExp,
           PyOpenCLPow,
           PyOpenCLId,
           PyOpenCLRound,
           PyOpenCLSquare,
           PyOpenCLSqrt,
           PyOpenCLGrad2D,
           PyOpenCLGrad3D,
           PyOpenCLCurl2D,
           PyOpenCLCurl3D]

contexts = [PyOpenCLContext]
