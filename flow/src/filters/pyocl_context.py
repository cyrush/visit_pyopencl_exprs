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
    import pyopencl as cl
    found_pyopencl = True
except ImportError:
    pass

__all__ = ["instance",
           "set_platform_id",
           "set_device_id",
           "clear_events",
           "add_event",
           "events_summary"]

from ..core import log

def info(msg):
    log.info(msg,"pyocl_context")

def nbytes_mb_gb(nbytes):
    mbytes = float(nbytes) * 9.53674e-7
    gbytes = mbytes * 0.000976562
    return mbytes, gbytes

def nbytes_str(nbytes):
    mbytes,gbytes = nbytes_mb_gb(nbytes)
    return "%d (MB: %s GB: %s)"  % (nbytes,repr(mbytes),repr(gbytes))


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
    ctx_info = ""
    device   = None
    events   = []
    @classmethod
    def set_platform_id(cls,plat_id):
        cls.plat_id = plat_id
    @classmethod
    def set_device_id(cls,dev_id):
        cls.dev_id = dev_id
    @classmethod
    def instance(cls):
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
    def device_memory(cls):
        return cls.device.global_mem_size
    @classmethod
    def clear_events(cls):
        cls.events = []
    @classmethod
    def add_event(cls,tag,cl_evnt,nbytes):
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


def set_platform_id(idx):
    PyOpenCLContextManager.set_platform_id(idx)

def set_device_id(idx):
    PyOpenCLContextManager.set_device_id(idx)

def device_memory():
    return PyOpenCLContextManager.device_memory()

def clear_events():
    PyOpenCLContextManager.clear_events()

def add_event(tag,cl_evnt,nbytes=0):
    PyOpenCLContextManager.add_event(tag,cl_evnt,nbytes)

def events_summary():
    return PyOpenCLContextManager.events_summary()

def instance():
    return PyOpenCLContextManager.instance()

