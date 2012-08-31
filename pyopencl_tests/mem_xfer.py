# example provided by Roger Pau Monn'e

import pyopencl as cl
import numpy
import numpy.linalg as la
import datetime
from time import time

import sys


def elapsed(event):
    return 1e-9*(event.profile.end - event.profile.start)

def exec_test(size):
    print "\nexec test w/ array size:%d" % size
    vin = numpy.random.rand(size).astype(numpy.float32)
    vout = numpy.empty_like(vin)
    for platform in cl.get_platforms():
        for device in platform.get_devices():
            print("===============================================================")
            print("Platform name:", platform.name)
            print("Platform profile:", platform.profile)
            print("Platform vendor:", platform.vendor)
            print("Platform version:", platform.version)
            print("---------------------------------------------------------------")
            print("Device name:", device.name)
            print("Device type:", cl.device_type.to_string(device.type))
            print("Device memory: ", device.global_mem_size//1024//1024, 'MB')
            print("Device max clock speed:", device.max_clock_frequency, 'MHz')
            print("Device compute units:", device.max_compute_units)

            # Simnple speed test
            ctx = cl.Context([device])
            queue = cl.CommandQueue(ctx, 
                                    properties=cl.command_queue_properties.PROFILING_ENABLE)

            mf = cl.mem_flags
            src_buf  = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=vin)
            dest_buf = cl.Buffer(ctx, mf.WRITE_ONLY, vout.nbytes)

            prg = cl.Program(ctx, """
                __kernel void xfer(__global const float *vin,
                                  __global float *vout)
                {
                            int gid = get_global_id(0);
                                    vout[gid] = vin[gid];
                }
                    """).build()
            xfer_in_evnt =  cl.enqueue_copy(queue,src_buf,vin)
            xfer_in_evnt.wait()
            xin_e = elapsed(xfer_in_evnt)
            print "xin:", xin_e
            exec_evt     =  prg.xfer(queue, vin.shape, None, src_buf, dest_buf)
            exec_evt.wait()
            exe_e = elapsed(exec_evt)
            print "kexe:", exe_e
            xfer_out_evnt = cl.enqueue_copy(queue, vout,dest_buf)
            xfer_out_evnt.wait()
            xout_e = elapsed(xfer_out_evnt)
            print "xout:", xout_e
            print "{'dv':%s,'sz': %d,'xin':%s,'kexe':%s,'xout':%s}" % (device.name,
                                                                       size,
                                                                       repr(xin_e),
                                                                       repr(exe_e),
                                                                       repr(xout_e))
            print "|csv, %s, %d, %s, %s, %s" % (device.name,
                                                  size,
                                                  repr(xin_e),
                                                  repr(exe_e),
                                                  repr(xout_e))                                                          
            error = 0
            for i in range(size):
                    if vout[i] != vin[i]:
                            error = 1
            if error:
                    print("Results doesn't match!!")
            else:
                    print("Results OK")

def mb_2_nfloat32(mb):
    return 1024*1024//4 * mb

if __name__ == "__main__":
    szes = [8,26,128]
    if len(sys.argv) > 3:
        szes = range(int(sys.argv[1]),int(sys.argv[2]),int(sys.argv[3]))
    for sz in szes:
        exec_test(mb_2_nfloat32(sz))

