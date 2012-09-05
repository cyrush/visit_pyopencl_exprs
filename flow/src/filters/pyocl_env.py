#
# ${disclaimer}
#
"""
 file: pyocl_context.py
 author: Cyrus Harrison <cyrush@llnl.gov>
 created: 4/21/2012
 description:
    Use lazy created singleton pyopencl context, to get around
    issues with the NVIDIA driver on edge.

"""

# Guarded import of pyopencl
found_pyopencl = False
try:
    import numpy as npy
    import pyopencl as cl
    found_pyopencl = True
except ImportError:
    pass

__all__ = ["Manager",
           "Pool"]

from ..core import log

def info(msg):
    log.info(msg,"pyocl_context")

def calc_nbytes(shape,dtype):
    res = npy.dtype(dtype).itemsize
    for s in shape:
        res*=s
    return res

def nbytes_mb_gb(nbytes):
    mbytes = float(nbytes) * 9.53674e-7
    gbytes = mbytes * 0.000976562
    return mbytes, gbytes

def nbytes_str(nbytes):
    mbytes, gbytes = nbytes_mb_gb(nbytes)
    return "%d (MB: %s GB: %s)"  % (nbytes,repr(mbytes),repr(gbytes))

class PyOpenCLBuffer(object):
    def __init__(self,id,shape,dtype):
        self.id        = id
        self.shape     = shape
        self.out_shape = shape
        self.dtype     = dtype
        self.nbytes    = calc_nbytes(shape,dtype)
        ctx = PyOpenCLContextManager.context()
        # TODO time alloc
        self.cl_obj   = cl.Buffer(ctx, cl.mem_flags.READ_WRITE, self.nbytes)
        self.__active = 2
        info("PyOpenCLBuffer create: " + str(self))
    def write(self,data):
        nbytes = calc_nbytes(data.shape,data.dtype)
        info("PyOpenCLBuffer write %s bytes to %s"  % (nbytes,str(self)))
        evnt = cl.enqueue_copy(PyOpenCLContextManager.queue(),self.cl_obj,data)
        PyOpenCLContextManager.add_event("win",evnt,nbytes)
        return evnt
    def read(self):
        nbytes = calc_nbytes(self.out_shape,self.dtype)
        info("PyOpenCLBuffer read %d bytes from %s " % (nbytes,str(self)))
        # TODO time alloc
        res = npy.zeros(self.out_shape,dtype=self.dtype)
        # this is blocking ...
        evnt = cl.enqueue_copy(PyOpenCLContextManager.queue(),res,self.cl_obj)
        PyOpenCLContextManager.add_event("rout",evnt,nbytes)
        evnt.wait()
        return res
    def active(self):
        return self.__active == 2
    def reactivate(self,out_shape,dtype):
        self.out_shape = out_shape
        self.dtype     = dtype
        self.__active  = 2
    def released(self):
        return self.__active == 1
    def release(self):
        info("PyOpenCLBuffer release: " + str(self))
        self.__active = 1
    def reclaim(self):
        self.__active = 0
    def available(self):
        return self.__active == 0
    def __str__(self):
        return "(%d) dtype: %s, nbytes: %s, alloc_shape: %s, out_shape: %s" % (self.id,self.dtype,self.nbytes,self.shape,self.out_shape)


class PyOpenCLBufferPool(object):
    buffers     = []
    total_alloc = 0
    @classmethod
    def reset(cls):
        # this should trigger pyopencl cleanup of buffers
        cls.buffers     = []
        cls.total_alloc = 0
    @classmethod
    def available_device_memory(cls,percentage=False):
        devm = PyOpenCLContextManager.device_memory()
        res  = devm - cls.total_alloc
        if percentage:
            res = round(100.0 * (float(res) / float(devm)),2)
        return res
    @classmethod
    def request_buffer(cls,shape,dtype):
        avail   = [b for b in cls.buffers if b.available()]
        rbytes  = calc_nbytes(shape,dtype)
        res_buf = None
        for b in avail:
            # first check for exact buffer size match
            if b.nbytes == rbytes:
                # we can reuse
                info("PyOpenCLBufferPool reuse: " + str(b))
                b.reactivate(shape,dtype)
                res_buf = b
                break
        if res_buf is None:
            for b in avail:
                # now simply check if the buffer is big enough
                if b.nbytes >= rbytes:
                    # we can reuse
                    info("PyOpenCLBufferPool reuse: " + str(b))
                    b.reactivate(shape,dtype)
                    res_buf = b
                    break
        if res_buf is None:
            res_buf = cls.__create_buffer(shape,dtype)
        cls.__release()
        return res_buf
    @classmethod
    def __create_buffer(cls,shape,dtype):
        # no suitable buffer, we need to create a new one
        ctx    = PyOpenCLContextManager.context()
        rbytes = calc_nbytes(shape,dtype)
        # see if we have enough bytes left on the device
        # if not, try to  reclaim some memory from released buffers
        if rbytes > cls.available_device_memory():
            cls.__reap(rbytes)
            if rbytes > cls.available_device_memory():
                msg  = "Reap failed\n"
                msg += " Free Request:       %s\n" % nbytes_str(rbytes)
                msg += " Result:             %s "  % nbytes_str(cls.available_device_memory())
                msg += "(" + repr(cls.available_device_memory(True)) + " %)\n"
                msg += "Total Device Memory: %s\n" % nbytes_str(device_memory())
                err(msg)
        res = PyOpenCLBuffer(len(cls.buffers),shape,dtype)
        cls.total_alloc += res.nbytes
        msg  = "PyOpenCLBufferPool total device memory alloced: "
        msg += nbytes_str(cls.total_alloc) +"\n"
        msg += "PyOpenCLBufferPool avaliable device memory: "
        msg += nbytes_str(cls.available_device_memory())
        msg += " (" + repr(cls.available_device_memory(True)) + "%)\n"
        info(msg)
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
        msg  = "PyOpenCLBufferPool reclaimed alloced: "
        msg += nbytes_str(rbytes)
        info(msg)



class PyOpenCLContextEvent(object):
    def __init__(self,tag,cl_evnt,nbytes):
        self.tag     = tag
        self.cl_evnt = cl_evnt
        self.nbytes  = nbytes
    def summary(self):
        qts = 1e-9*(self.cl_evnt.profile.submit - self.cl_evnt.profile.queued)
        sts = 1e-9*(self.cl_evnt.profile.start  - self.cl_evnt.profile.submit)
        ste = 1e-9*(self.cl_evnt.profile.end    - self.cl_evnt.profile.start)
        qte = 1e-9*(self.cl_evnt.profile.end    - self.cl_evnt.profile.queued)
        res = "Event: %s (nbytes=%d)\n" % (self.tag,self.nbytes)
        res += "  Queued to Submit: %s\n" % repr(qts)
        res += "  Submit to Start:  %s\n" % repr(sts)
        res += "  Start  to End:    %s\n" % repr(ste)
        res += " Queued to End:     %s\n" % repr(qte)
        return res
    def queued_to_end(self):
        return 1e-9*(self.cl_evnt.profile.end - self.cl_evnt.profile.queued)
    def start_to_end(self):
        return 1e-9*(self.cl_evnt.profile.end - self.cl_evnt.profile.start)

class PyOpenCLContextManager(object):
    plat_id  = 0
    dev_id   = 0
    ctx      = None
    ctx_info = None
    device   = None
    cmdq     = None
    events   = []
    @classmethod
    def set_platform_id(cls,plat_id):
        cls.plat_id = plat_id
    @classmethod
    def set_device_id(cls,dev_id):
        cls.dev_id = dev_id
    @classmethod
    def queue(cls):
        if cls.cmdq is None:
            ctx = cls.context()
            cls.cmdq = cl.CommandQueue(ctx,
                        properties=cl.command_queue_properties.PROFILING_ENABLE)
        return cls.cmdq
    @classmethod
    def instance(cls):
        return cls.context()
    @classmethod
    def context(cls):
        if not found_pyopencl:
            return None
        if cls.ctx is None:
            platform = cl.get_platforms()[cls.plat_id]
            device = platform.get_devices()[cls.dev_id]
            cinfo  = "OpenCL Context Info\n"
            cinfo += " Using platform id = %d\n" % cls.plat_id
            cinfo += "  Platform name: %s\n" % platform.name
            cinfo += "  Platform profile: %s\n" % platform.profile
            cinfo += "  Platform vendor: %s\n" % platform.vendor
            cinfo += "  Platform version: %s\n" % platform.version
            cinfo += " Using device id = %d\n" % cls.dev_id
            cinfo += "  Device name: %s\n" % device.name
            cinfo += "  Device type: %s\n" % cl.device_type.to_string(device.type)
            cinfo += "  Device memory: %s\n" % device.global_mem_size
            cinfo += "  Device max clock speed: %s MHz\n" % device.max_clock_frequency
            cinfo += "  Device compute units: %s\n" % device.max_compute_units
            info(cinfo)
            cls.device = device
            cls.ctx = cl.Context([device])
            cls.ctx_info = cinfo
        return cls.ctx
    @classmethod
    def dispatch_kernel(cls,kernel_source,out_shape,buffers):
        ibuffs = [ b.cl_obj for b in buffers]
        prg    = cl.Program(cls.context(),kernel_source).build()
        # TODO change kmain?
        evnt   = prg.kmain(cls.queue(), out_shape, None, *ibuffs)
        cls.add_event("kexec",evnt)
        return evnt
    @classmethod
    def device_memory(cls):
        return cls.device.global_mem_size
    @classmethod
    def clear_events(cls):
        cls.events = []
    @classmethod
    def add_event(cls,tag,cl_evnt,nbytes=0):
        cls.events.append(PyOpenCLContextEvent(tag,cl_evnt,nbytes))
    @classmethod
    def events_summary(cls):
        res      = ""
        tbytes   = 0
        ttag     = {}
        tqte     = 0.0
        tnevents = len(cls.events)
        for e in cls.events:
            tbytes += e.nbytes
            tqte   += e.queued_to_end()
            if e.tag in ttag.keys():
                t = ttag[e.tag]
                t["nevents"] += 1
                t["nbytes"] += e.nbytes
                t["qte"]    += e.queued_to_end()
                t["ste"]    += e.start_to_end()
            else:
                ttag[e.tag] = {"nevents":1,
                               "nbytes":e.nbytes,
                               "qte":e.queued_to_end(),
                               "ste":e.start_to_end()}
        tmbytes, tgbytes = nbytes_mb_gb(tbytes)
        res += cls.ctx_info
        res += "Tag Totals:\n"
        for k,v in ttag.items():
            nevents = v["nevents"]
            nbytes  = v["nbytes"]
            qte     = v["qte"]
            ste     = v["ste"]
            nmbytes, ngbytes = nbytes_mb_gb(nbytes)
            avg_bytes = nbytes / float(nevents)
            avg_mbytes, avg_gbytes =  nbytes_mb_gb(avg_bytes)
            gbps    = ngbytes / ste
            v["avg_bytes"]  = avg_bytes
            v["gbps"]       = gbps
            res += " Tag: %s\n" % k
            res += "  Total # of events: %d\n" % nevents
            res += "  Total queued to end: %s (s)\n" % repr(qte)
            res += "  Total start  to end: %s (s)\n" % repr(ste)
            res += "  Total nbytes: %s\n" % nbytes_str(nbytes)
            res += "  Total gb/s: %s [ngbytes / ste]\n" % repr(gbps)
            res += "  Average nbytes: %s\n" % nbytes_str(avg_bytes)
        res += "Total # of events: %d\n" % tnevents
        res += "Total nbytes: %s\n" % nbytes_str(tbytes)
        res += "Total queued to end: %s (s)\n" % repr(tqte)
        ttag["total"] = {"nevents": tnevents,
                         "nbytes":  tbytes,
                         "qte":     tqte}
        return res


Manager = PyOpenCLContextManager
Pool    = PyOpenCLBufferPool
