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
# import logging
# logging.basicConfig(level=logging.INFO)

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
    log.info(msg,"filters.pyocl_batch")


class PyOpenCLBatchBuffer(object):
    def __init__(self,id,context,shape,dtype):
        self.context = context
        self.id = id
        self.shape     = shape
        self.out_shape = shape
        self.dtype  = dtype
        self.nbytes = PyOpenCLBatchBuffer.calc_nbytes(shape,dtype)
        ctx = pyocl_context.instance()
        self.cl_obj  = cl.Buffer(ctx, cl.mem_flags.READ_WRITE, self.nbytes)
        self.__active = 2
        log.info("PyOpenCLBatchBuffer create: " + str(self))
    def active(self):
        return self.__active == 2
    def released(self):
        return self.__active == 1
    def available(self):
        return self.__active == 0
    def write(self,data):
        nbytes = self.calc_nbytes(data.shape,data.dtype)
        log.info("PyOpenCLBatchBuffer write %s bytes to %s"  % (nbytes,str(self)))
        evnt = cl.enqueue_copy(self.context.queue(),self.cl_obj,data)
        pyocl_context.add_event("win",evnt,nbytes)
        return evnt
    def read(self):
        nbytes = self.calc_nbytes(self.out_shape,self.dtype)
        log.info("PyOpenCLBatchBuffer read %d bytes from %s " % (nbytes,str(self)))
        # this is blocking ...
        res = npy.zeros(self.out_shape,dtype=self.dtype)
        evnt = cl.enqueue_copy(self.context.queue(),res,self.cl_obj)
        pyocl_context.add_event("rout",evnt,nbytes)
        evnt.wait()
        return res
    def release(self):
        log.info("PyOpenCLBatchBuffer release: " + str(self))
        self.__active = 1
    def reclaim(self):
        self.__active = 0
    def reactivate(self,out_shape,dtype):
        self.out_shape = out_shape
        self.dtype     = dtype
        self.__active  = 2
    def __str__(self):
        return "(%d) dtype: %s, nbytes: %s, alloc_shape: %s, out_shape: %s" % (self.id,self.dtype,self.nbytes,self.shape,self.out_shape)
    @classmethod
    def calc_nbytes(cls,shape,dtype):
        res = npy.dtype(dtype).itemsize
        for s in shape:
            res*=s;
        return res;

class PyOpenCLBatchBufferPool(object):
    buffers     = []
    total_alloc = 0
    @classmethod
    def reset(cls):
        # this should trigger cleanup
        cls.total_alloc = 0
        cls.buffers     = []
    @classmethod
    def available_device_memory(cls,percentage=False):
        devm = pyocl_context.device_memory() 
        res  = devm - cls.total_alloc
        if percentage:
            res = float(res) / float(devm)
        return res
    @classmethod
    def request_buffer(cls,context,shape,dtype):
        avail   = [b for b in cls.buffers if b.available()]
        rbytes  = PyOpenCLBatchBuffer.calc_nbytes(shape,dtype)
        res_buf = None
        for b in avail:
            # check if the buffer is big enough
            if b.nbytes >= rbytes:
                # we can reuse
                log.info("PyOpenCLBatchBufferPool reuse: " + str(b))
                b.reactivate(shape,dtype)
                res_buf = b
                break
        if res_buf is None:
            res_buf = cls.__create_buffer(context,shape,dtype)
        cls.__release()
        return res_buf
    @classmethod
    def __create_buffer(cls,context,shape,dtype):
        # no suitable buffer, we need to create a new one
        ctx = pyocl_context.instance()
        rbytes = PyOpenCLBatchBuffer.calc_nbytes(shape,dtype)
        # see if we have enough bytes left on the device
        # if not, try to  reclaim some memory from released buffers
        if rbytes > cls.available_device_memory():
            cls.__reap(rbytes)
            if rbytes > cls.available_device_memory():
                msg = "<ERROR> Reap failed\n\n request: %s\n result: %s"
                msg = msg % (pyocl_context.nbytes_str(rbytes),
                         pyocl_context.nbytes_str(avail_bytes))
                log.info(msg)
        res = PyOpenCLBatchBuffer(len(cls.buffers),context,shape,dtype)
        cls.total_alloc += res.nbytes
        msg  = "PyOpenCLBatchBufferPool total device memory alloced: "
        msg += pyocl_context.nbytes_str(cls.total_alloc) +"\n"
        msg += "PyOpenCLBatchBufferPool avaliable device memory: "
        msg += pyocl_context.nbytes_str(cls.available_device_memory())
        msg += " (" + repr(cls.available_device_memory(True)) + "%)\n"
        log.info(msg)
        cls.buffers.append(res)
        return res
    @classmethod
    def __release(cls):
        #if released(), the buffer is avail for the next request
        for b in cls.buffers:
            if b.released(): 
                b.reclaim()
    @classmethod
    def __reap(cls,nbytes):
        rbytes = 0
        avail  = [b for b in cls.buffers if b.available()]
        for b in avail:
            cls.total_alloc -= b.nbytes
            rbytes += b.nbytes
            cls.buffers.remove(b)
            if cls.available_device_memory() >= nbytes:
                # we have enough mem, so break
                break
        del avail
        msg  = "PyOpenCLBatchBufferPool reclaimed alloced: "
        msg += pyocl_context.nbytes_str(rbytes)
        log.info(msg)



class PyOpenCLBatchContext(Context):
    context_type = "pyocl_batch"
    def start(self,dev_id = 0):
        pyocl_context.set_device_id(dev_id)
        pyocl_context.clear_events()
        PyOpenCLBatchBufferPool.reset()
        self.__queue = None
    def set_device_id(self,dev_id):
        pyocl_context.set_device_id(dev_id)
    def queue(self):
        if self.__queue is None:
            ctx = pyocl_context.instance()
            self.__queue = cl.CommandQueue(ctx, properties=cl.command_queue_properties.PROFILING_ENABLE)
        return self.__queue
    def execute_kernel(self,kernel_source,inputs,out_dim=None):
        ctx = pyocl_context.instance()
        msg  = "Execute Kernel:\n"
        msg += kernel_source
        info(msg)
        buffers = []
        vshape = self.__find_valid_shape(inputs)
        if out_dim is None:
            out_shape = vshape
        else:
            if out_dim == 1:
                out_shape = (vshape[0],)
            else:
                out_shape = (vshape[0],out_dim)
        info("Execute Kernel: out_shape = " + str(out_shape))
        for ipt in inputs:
            if isinstance(ipt,PyOpenCLBatchBuffer):
                buffers.append(ipt.cl_obj)
            else:
                cary = npy.zeros(out_shape,dtype=npy.float32)
                cary.fill(ipt)
                const_buf = PyOpenCLBatchBufferPool.request_buffer(self,out_shape,npy.float32)
                const_buf.write(cary)
                buffers.append(const_buf.cl_obj)
        dest_buf = PyOpenCLBatchBufferPool.request_buffer(self,out_shape,npy.float32)
        buffers.append(dest_buf.cl_obj)
        prg = cl.Program(ctx,kernel_source).build()
        evnt = prg.kmain(self.queue(), out_shape, None, *buffers)
        pyocl_context.add_event("kmain",evnt)
        return dest_buf
    def events_summary(self):
        return pyocl_context.events_summary()
    def __find_valid_shape(self,inputs):
        for ipt in inputs:
            if isinstance(ipt,PyOpenCLBatchBuffer):
                return ipt.out_shape
        return None

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
        buf = PyOpenCLBatchBufferPool.request_buffer(self.context,data.shape,data.dtype)
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
        #data = a.read()
        #buf = PyOpenCLBatchBufferPool.request_buffer(self.context,(data.shape[0],),npy.float32)
        #buf.write(npy.array(data[:,p.index]))
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
    default_params = {"value":0}
    input_ports    = []
    output_port    = True
    def execute(self):
        p = self.params
        return p.value

#class PyOpenCLBatchConst(Filter):
    #filter_type    = "const"
    #default_params = {"value":0.0}
    #input_ports    = []
    #output_port    = True
    #def execute(self):
        #p = self.params
        #kernel_source =  """
            #__kernel void kmain(__global float *o)
            #{
              #o[get_global_id(0)] =  %s;
            #}
            #""" % str(p.value)
        #return self.context.execute_kernel(kernel_source,inputs)


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

