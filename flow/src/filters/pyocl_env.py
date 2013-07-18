#*****************************************************************************
#
# Copyright (c) 2000 - 2012, Lawrence Livermore National Security, LLC
# Produced at the Lawrence Livermore National Laboratory
# LLNL-CODE-442911
# All rights reserved.
#
# This file is  part of VisIt. For  details, see https://visit.llnl.gov/.  The
# full copyright notice is contained in the file COPYRIGHT located at the root
# of the VisIt distribution or at http://www.llnl.gov/visit/copyright.html.
#
# Redistribution  and  use  in  source  and  binary  forms,  with  or  without
# modification, are permitted provided that the following conditions are met:
#
#  - Redistributions of  source code must  retain the above  copyright notice,
#    this list of conditions and the disclaimer below.
#  - Redistributions in binary form must reproduce the above copyright notice,
#    this  list of  conditions  and  the  disclaimer (as noted below)  in  the
#    documentation and/or other materials provided with the distribution.
#  - Neither the name of  the LLNS/LLNL nor the names of  its contributors may
#    be used to endorse or promote products derived from this software without
#    specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT  HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR  IMPLIED WARRANTIES, INCLUDING,  BUT NOT  LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND  FITNESS FOR A PARTICULAR  PURPOSE
# ARE  DISCLAIMED. IN  NO EVENT  SHALL LAWRENCE  LIVERMORE NATIONAL  SECURITY,
# LLC, THE  U.S.  DEPARTMENT OF  ENERGY  OR  CONTRIBUTORS BE  LIABLE  FOR  ANY
# DIRECT,  INDIRECT,   INCIDENTAL,   SPECIAL,   EXEMPLARY,  OR   CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT  LIMITED TO, PROCUREMENT OF  SUBSTITUTE GOODS OR
# SERVICES; LOSS OF  USE, DATA, OR PROFITS; OR  BUSINESS INTERRUPTION) HOWEVER
# CAUSED  AND  ON  ANY  THEORY  OF  LIABILITY,  WHETHER  IN  CONTRACT,  STRICT
# LIABILITY, OR TORT  (INCLUDING NEGLIGENCE OR OTHERWISE)  ARISING IN ANY  WAY
# OUT OF THE  USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH
# DAMAGE.
#*****************************************************************************
"""
 file: pyocl_env.py
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

from ..core import WallTimer, log


def info(msg):
    log.info(msg,"pyocl_env")

def err(msg):
    log.error(msg,"pyocl_env")

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
    def __init__(self,id,shape,dtype,pool):
        self.id        = id
        self.shape     = shape
        self.out_shape = shape
        self.dtype     = dtype
        self.nbytes    = calc_nbytes(shape,dtype)
        self.pool      = pool
        ctx = self.pool.context
        balloc = PyOpenCLHostTimer("balloc",self.nbytes)
        balloc.start()
        self.cl_obj   = cl.Buffer(ctx.context(), cl.mem_flags.READ_WRITE, self.nbytes)
        balloc.stop()
        ctx.add_host_event(balloc)
        self.__active = 2
        info("PyOpenCLBuffer create: " + str(self))
    def write(self,data):
        nbytes = calc_nbytes(data.shape,data.dtype)
        info("PyOpenCLBuffer write %s bytes to %s"  % (nbytes,str(self)))
        evnt = cl.enqueue_copy(self.pool.context.queue(),self.cl_obj,data)
        self.pool.context.add_event("win",evnt,nbytes)
        return evnt
    def read(self):
        nbytes = calc_nbytes(self.out_shape,self.dtype)
        info("PyOpenCLBuffer read %d bytes from %s " % (nbytes,str(self)))
        htimer = PyOpenCLHostTimer("ralloc",self.nbytes)
        htimer.start()
        res = npy.zeros(self.out_shape,dtype=self.dtype)
        htimer.stop()
        self.pool.context.add_host_event(htimer)
        # this is blocking ...
        evnt = cl.enqueue_copy(self.pool.context.queue(),res,self.cl_obj)
        self.pool.context.add_event("rout",evnt,nbytes)
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
        res = "(%d) dtype: %s, nbytes: %s, alloc_shape: %s, out_shape: %s status:%d"
        res = res % (self.id,self.dtype,self.nbytes,self.shape,self.out_shape,self.__active)
        return res


class PyOpenCLBufferPool(object):
    def __init__(self,context):
        self.context     = context
        self.buffers     = []
        self.total_alloc = 0
    def reset(self):
        rset = PyOpenCLHostTimer("pool_reset",0)
        rset.start()
        # this should trigger pyopencl cleanup of buffers
        self.buffers     = []
        self.total_alloc = 0
        self.max_alloc   = 0
        rset.stop()
        self.context.add_host_event(rset)
    def available_device_memory(self,percentage=False):
        devm = self.context.device_memory()
        res  = devm - self.total_alloc
        if percentage:
            res = round(100.0 * (float(res) / float(devm)),2)
        return res
    def device_memory_high_water(self):
        return self.max_alloc
    def request_buffer(self,shape,dtype):
        avail   = [b for b in self.buffers if b.available()]
        rbytes  = calc_nbytes(shape,dtype)
        res_buf = None
        for b in avail:
            # first check for exact buffer size match
            if b.nbytes == rbytes:
                # we can reuse
                dreuse = PyOpenCLHostTimer("dreuse",b.nbytes)
                dreuse.start()
                info("PyOpenCLBufferPool reuse: " + str(b))
                b.reactivate(shape,dtype)
                res_buf = b
                dreuse.stop()
                self.context.add_host_event(dreuse)
                break
        if res_buf is None:
            res_buf = self.__create_buffer(shape,dtype)
        return res_buf
    def buffer_info(self):
        res  = "Total Device Memory: %s\n" % nbytes_str(self.context.device_memory())
        res += "Available Memory:   %s "  % nbytes_str(self.available_device_memory())
        res += "(" + repr(self.available_device_memory(True)) + " %)\n"
        res += "Buffers:\n"
        for b in self.buffers:
            res += " " + str(b) + "\n"
        return res
    def reclaim(self):
        #if released(), the buffer is avail for the next request
        for b in self.buffers:
            if b.released():
                b.reclaim()
    def release_buffer(self,buff):
        drel = PyOpenCLHostTimer("drelease",buff.nbytes)
        drel.start()
        self.total_alloc -= buff.nbytes
        self.buffers.remove(buff)
        drel.stop()
        self.context.add_host_event(drel)
    def __create_buffer(self,shape,dtype):
        # no suitable buffer, we need to create a new one
        rbytes = calc_nbytes(shape,dtype)
        # see if we have enough bytes left on the device
        # if not, try to  reclaim some memory from released buffers
        # if rbytes > cls.available_device_memory():
        self.__reap(rbytes)
        if rbytes > self.available_device_memory():
            msg  = "Reap failed\n"
            msg += " Free Request:       %s\n" % nbytes_str(rbytes)
            msg += self.context.events_summary()[0] + "\n"
            msg += self.buffer_info() + "\n"
            err(msg)
            raise MemoryError
        res = PyOpenCLBuffer(len(self.buffers),shape,dtype,self)
        self.total_alloc += res.nbytes
        if self.total_alloc > self.max_alloc:
            self.max_alloc = self.total_alloc
        self.buffers.append(res)
        info(self.buffer_info())
        return res
    def __reap(self,nbytes):
        rbytes = 0
        avail  = [b for b in self.buffers if b.available()]
        for b in avail:
            rbytes += b.nbytes
            self.release_buffer(b)
            if self.available_device_memory() >= nbytes:
                # we have enough mem, so break
                break
        del avail
        msg  = "PyOpenCLBufferPool reap reclaimed: "
        msg += nbytes_str(rbytes)
        info(msg)


class PyOpenCLContextEvent(object):
    def __init__(self,tag,cl_evnt,nbytes):
        self.etype   = "device"
        self.tag     = tag
        self.cl_evnt = cl_evnt
        self.nbytes  = nbytes
    def summary(self):
        qts = 1e-9*(self.cl_evnt.profile.submit - self.cl_evnt.profile.queued)
        sts = 1e-9*(self.cl_evnt.profile.start  - self.cl_evnt.profile.submit)
        ste = 1e-9*(self.cl_evnt.profile.end    - self.cl_evnt.profile.start)
        qte = 1e-9*(self.cl_evnt.profile.end    - self.cl_evnt.profile.queued)
        res = "Device Event: %s (nbytes=%d)\n" % (self.tag,self.nbytes)
        res += "  Queued to Submit: %s\n" % repr(qts)
        res += "  Submit to Start:  %s\n" % repr(sts)
        res += "  Start  to End:    %s\n" % repr(ste)
        res += " Queued to End:     %s\n" % repr(qte)
        return res
    def queued_to_end(self):
        return 1e-9*(self.cl_evnt.profile.end - self.cl_evnt.profile.queued)
    def start_to_end(self):
        return 1e-9*(self.cl_evnt.profile.end - self.cl_evnt.profile.start)


class PyOpenCLHostTimer(WallTimer):
    def __init__(self,tag,nbytes):
        super(PyOpenCLHostTimer,self).__init__(tag)
        self.etype   = "host"
        self.nbytes  = nbytes
    def summary(self):
        res = "Host Event: %s (nbytes=%d)\n" % (self.tag,self.nbytes)
        res += "  Start  to End:    %s\n" % repr(self.start_to_end())
        return res
    def queued_to_end(self):
        return self.get_elapsed()
    def start_to_end(self):
        return self.get_elapsed()

class PyOpenCLContextManager(object):
    contexts = {}
    # context pass thrus
    @classmethod
    def select_device(cls,platform_id, device_id,context_name="default"):
        cls.contexts[context_name] = PyOpenCLContext(context_name,platform_id,device_id)
    @classmethod
    def context(cls,context_name="default"):
        cls.contexts[context_name].context()
        return cls.contexts[context_name]
    @classmethod
    def queue(cls,context_name="default"):
        ctx = cls.context(context_name)
        return ctx.queue()
    @classmethod
    def clear_events(cls,context_name="default"):
        ctx = cls.context(context_name)
        return ctx.clear_events()
    @classmethod
    def dispatch_kernel(cls,kernel_source,out_shape,buffers,context_name="default"):
        ctx = cls.context(context_name)
        return ctx.dispatch_kernel(kernel_source,out_shape,buffers)
    @classmethod
    def add_host_event(cls,host_timer,context_name="default"):
        ctx = cls.context(context_name)
        return ctx.add_host_event(host_timer)
    @classmethod
    def add_event(cls,tag,cl_evnt,nbytes=0,context_name="default"):
        ctx = cls.context(context_name)
        return ctx.add_event(tag,cl_evnt,nbytes)
    @classmethod
    def events_summary(cls,context_name="default"):
        ctx = cls.context(context_name)
        return ctx.events_summary()
    # pool pass thrus
    @classmethod
    def reset(cls,context_name="default"):
        ctx = cls.context(context_name)
        return ctx.pool.reset()
    @classmethod
    def request_buffer(cls,shape,dtype,context_name="default"):
        ctx = cls.context(context_name)
        return ctx.pool.request_buffer(shape,dtype)
    @classmethod 
    def reclaim(cls,context_name="default"):
        ctx = cls.context(context_name)
        return ctx.pool.reclaim()
        

class PyOpenCLContext(object):
    def __init__(self,context_name,platform_id,device_id):
        self.name       = context_name
        self.plat_id    = platform_id
        self.dev_id     = device_id
        self.ctx        = None
        self.info       = None
        self.device     = None
        self.cmdq       = None
        self.pool       = None
        self.events     = []
    def queue(self):
        if self.cmdq is None:
            ctx = self.context()
            prof = cl.command_queue_properties.PROFILING_ENABLE
            self.cmdq = cl.CommandQueue(ctx,properties=prof)
        return self.cmdq
    def context(self):
        if not found_pyopencl:
            return None
        if self.ctx is None:
            csetup = PyOpenCLHostTimer("ctx_setup",0)
            csetup .start()
            platform = cl.get_platforms()[self.plat_id]
            device = platform.get_devices()[self.dev_id]
            cinfo  = "OpenCL Context Info\n"
            cinfo += " Using platform id = %d\n" % self.plat_id
            cinfo += "  Platform name: %s\n" % platform.name
            cinfo += "  Platform profile: %s\n" % platform.profile
            cinfo += "  Platform vendor: %s\n" % platform.vendor
            cinfo += "  Platform version: %s\n" % platform.version
            cinfo += " Using device id = %d\n" % self.dev_id
            cinfo += "  Device name: %s\n" % device.name
            cinfo += "  Device type: %s\n" % cl.device_type.to_string(device.type)
            cinfo += "  Device memory: %s\n" % device.global_mem_size
            cinfo += "  Device max clock speed: %s MHz\n" % device.max_clock_frequency
            cinfo += "  Device compute units: %s\n" % device.max_compute_units
            info(cinfo)
            self.device = device
            self.ctx = cl.Context([device])
            self.ctx_info = cinfo
            self.pool = PyOpenCLBufferPool(self)
            csetup.stop()
            self.add_host_event(csetup)
        return self.ctx
    def dispatch_kernel(self,kernel_source,out_shape,buffers):
        kdisp = PyOpenCLHostTimer("kdispatch",0)
        kdisp.start()
        ibuffs = [ b.cl_obj for b in buffers]
        prg    = cl.Program(self.context(),kernel_source).build()
        evnt   = prg.kmain(self.queue(), out_shape, None, *ibuffs)
        self.add_event("kexec",evnt)
        kdisp.stop()
        self.add_host_event(kdisp)
        return evnt
    def device_memory(self):
        self.context()
        return self.device.global_mem_size
    def clear_events(self):
        self.events = []
    def add_event(self,tag,cl_evnt,nbytes=0):
        self.events.append(PyOpenCLContextEvent(tag,cl_evnt,nbytes))
    def add_host_event(self,host_timer):
        self.events.append(host_timer)
    def events_summary(self):
        res      = ""
        tbytes   = 0
        ttag     = {}
        tqte     = 0.0
        tste     = 0.0
        tnevents = len(self.events)
        maxalloc = self.pool.device_memory_high_water()
        for e in self.events:
            tbytes += e.nbytes
            tqte   += e.queued_to_end()
            tste   += e.start_to_end()
            if e.tag in ttag.keys():
                t = ttag[e.tag]
                t["nevents"] += 1
                t["nbytes"] += e.nbytes
                t["qte"]    += e.queued_to_end()
                t["ste"]    += e.start_to_end()
            else:
                ttag[e.tag] = {"tag": e.tag,
                               "etype": e.etype,
                               "nevents":1,
                               "nbytes":e.nbytes,
                               "qte":e.queued_to_end(),
                               "ste":e.start_to_end()}
        tmbytes, tgbytes = nbytes_mb_gb(tbytes)
        res += self.ctx_info
        res += "\nTag Totals:\n"
        for k,v in ttag.items():
            nevents = v["nevents"]
            etype   = v["etype"]
            nbytes  = v["nbytes"]
            qte     = v["qte"]
            ste     = v["ste"]
            nmbytes, ngbytes = nbytes_mb_gb(nbytes)
            avg_bytes = nbytes / float(nevents)
            avg_mbytes, avg_gbytes =  nbytes_mb_gb(avg_bytes)
            gbps    = ngbytes / ste
            v["avg_bytes"]  = avg_bytes
            v["gbps"]       = gbps
            res += " Tag: %s (%s)\n" % (k ,etype)
            res += "  Total # of events: %d\n" % nevents
            res += "  Total queued to end: %s (s)\n" % repr(qte)
            res += "  Total start  to end: %s (s)\n" % repr(ste)
            res += "  Total nbytes: %s\n" % nbytes_str(nbytes)
            res += "  Total gb/s: %s [ngbytes / ste]\n" % repr(gbps)
            res += "  Average nbytes: %s\n" % nbytes_str(avg_bytes)
            res += "%s\n" % v
        res += "Total # of events: %d\n" % tnevents
        res += "Total nbytes: %s\n" % nbytes_str(tbytes)
        res += "Total start to end:  %s (s)\n" % repr(tqte)
        res += "Total queued to end: %s (s)\n" % repr(tste)
        res += "Dev max alloc: %s \n" % nbytes_str(maxalloc)
        ttag["total"] = {"tag":"total",
                         "etype":"total",
                         "nevents": tnevents,
                         "nbytes":  tbytes,
                         "qte":     tqte,
                         "ste":     tste,
                         "dev_max_alloc": maxalloc}
        res += "%s\n" % ttag["total"]
        return res, ttag


Manager = PyOpenCLContextManager
Pool    = PyOpenCLContextManager
