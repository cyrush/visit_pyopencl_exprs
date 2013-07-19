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
 file: test_filters_pyocl_ops.py
 author: Cyrus Harrison <cyrush@llnl.gov>
 created: 3/24/2012
 description:
    unittest test cases for Filters in the pyocl_ops module.

"""

import unittest
try:
    import numpy as npy
except:
    pass

from flow import *
from flow.filters import pyocl_env

from decorators import pyocl_test

# uncomment for detailed exe info
#import logging
#logging.basicConfig(level=logging.INFO)

ksrc = """
       __kernel void kmain(__global const float *a,
       __global const float *b, __global float *c)
       {
        int gid = get_global_id(0);
        c[gid] = a[gid] + b[gid];
       }
       """


class TestPyOpenCLOps(unittest.TestCase):
    def setUp(self):
        print ""
    @pyocl_test
    def test_01_pyocl_dispatch(self):
        pyocl_env.Manager.select_device(0,0)
        v_a = npy.array(range(10),dtype=npy.float32)
        v_b = npy.array(range(10),dtype=npy.float32)
        dest_buf = pyocl_env.Pool.request_buffer(v_a.shape,v_a.dtype)
        buffers = [pyocl_env.Pool.request_buffer(v_a.shape,v_a.dtype),
                   pyocl_env.Pool.request_buffer(v_a.shape,v_a.dtype),
                   dest_buf]
        buffers[0].write(v_a)
        buffers[1].write(v_b)
        pyocl_env.Manager.dispatch_kernel(ksrc,
                                          v_a.shape,
                                          buffers)
        act_res = dest_buf.read()
        test_res = v_a + v_b;
        dsum = npy.sum(act_res - test_res)
        print "CL Kernel Result:    %s" % str(act_res)
        print "Test Result:         %s" % str(test_res)
        print "Difference:          %s" % str(dsum)
        self.assertTrue(dsum < 1e-6)
    @pyocl_test
    def test_02_multi_context(self):
        # note: this runs on all avail devices
        v_a = npy.array(range(10),dtype=npy.float32)
        v_b = npy.array(range(10),dtype=npy.float32)
        
        devs = pyocl_env.Manager.devices()
        print devs
        for d in devs:
            plat_id,dev_id,ctx_name =  d
            pyocl_env.Manager.select_device(plat_id,dev_id,ctx_name)           
            dest_buf = pyocl_env.Pool.request_buffer(v_a.shape,v_a.dtype,ctx_name)
            buffers = [pyocl_env.Pool.request_buffer(v_a.shape,v_a.dtype,ctx_name),
                       pyocl_env.Pool.request_buffer(v_a.shape,v_a.dtype,ctx_name),
                   dest_buf]
            buffers[0].write(v_a)
            buffers[1].write(v_b)
            pyocl_env.Manager.dispatch_kernel(ksrc,
                                              v_a.shape,
                                              buffers,ctx_name)
            act_res = dest_buf.read()
            test_res = v_a + v_b;
            dsum = npy.sum(act_res - test_res)
            print "Test device %s" % str(d)
            print "CL Kernel Result:    %s" % str(act_res)
            print "Test Result:         %s" % str(test_res)
            print "Difference:          %s" % str(dsum)
            self.assertTrue(dsum < 1e-6)


if __name__ == '__main__':
    unittest.main()

