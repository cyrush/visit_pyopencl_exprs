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

__all__ = ["instance"]

from ..core import log

def info(msg):
    log.info(msg,"pyocl_context")

class PyOpenCLContextManager(object):
    dev_id = 0
    ctx    = None
    @classmethod
    def set_device_id(cls,dev_id):
        cls.dev_id = dev_id
    @classmethod
    def instance(cls):
        if not found_pyopencl:
            return None
        if cls.ctx is None:
            platform = cl.get_platforms()[0]
            device   = platform.get_devices()[cls.dev_id]
            info("Platform name: %s" % platform.name)
            info("Platform profile: %s" % platform.profile)
            info("Platform vendor: %s" % platform.vendor)
            info("Platform version: %s" % platform.version)
            info("Device name: %s" % device.name)
            info("Device type: %s" % cl.device_type.to_string(device.type))
            info("Device memory: %s" % device.global_mem_size)
            info("Device max clock speed: %s MHz" % device.max_clock_frequency)
            info("Device compute units: %s" % device.max_compute_units)
            cls.ctx = cl.Context([device])
        return cls.ctx

def set_device_id(idx):
    PyOpenCLContextManager.set_device_id(idx)

def instance():
    return PyOpenCLContextManager.instance()

