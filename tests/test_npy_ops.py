#!/usr/bin/env python
#
# ${disclaimer}
#
"""
 file: test_npy_ops.py
 author: Cyrus Harrison <cyrush@llnl.gov>
 created: 12/09/2011
 description:
    TODO

"""

import unittest
import numpy as npy

from flow.core import *
from flow.filters import npy_ops

class TestNPyOps(unittest.TestCase):
    def test_01_simple_workspace(self):
        w = Workspace()
        w.register_filters(npy_ops)
        v_a = npy.array(range(10),dtype=npy.double)
        v_b = npy.array(range(10),dtype=npy.double)
        w.add("src","src_a",{"data":v_a})
        w.add("src","src_b",{"data":v_b})
        w.add("add","f1")
        w.add("sub","f2")
        w.add("mult","f3")
        w.add("mult","f4")
        w.add("add","f5")
        # f1 = src_a + src_b
        w.connect("src_a","f1:a")
        w.connect("src_b","f1:b")
        # f2 = src_b - src_a
        w.connect("src_b","f2:a")
        w.connect("src_a","f2:b")
        # f3 = f1^2
        w.connect("f1","f3:a")
        w.connect("f1","f3:b")
        # f4 = f2^2
        w.connect("f2","f4:a")
        w.connect("f2","f4:b")
        # f5 = f4 + f3
        w.connect("f3","f5:a")
        w.connect("f4","f5:b")
        print ""
        w.execute()
        act_res = w.registry_fetch("f5")
        # get output and test
        test_res = npy.power((v_a + v_b),2.0)+ npy.power((v_a - v_b),2.0)
        dsum = npy.sum(act_res - test_res)
        print "Filter Graph Result: %s" % str(act_res)
        print "Test Result:         %s" % str(test_res)
        print "Difference:          %s" % str(dsum)
        self.assertTrue(dsum < 1e-6)
    def test_02_more_ops(self):
        w = Workspace()
        w.register_filters(npy_ops)
        v_a = npy.array(range(10),dtype=npy.double)
        v_b = npy.array(range(10),dtype=npy.double)
        v_p = npy.array([2]*10,dtype=npy.double)
        w.add("src","src_a",{"data":v_a})
        w.add("src","src_b",{"data":v_b})
        w.add("src","src_p",{"data":v_p})
        w.add("add","f1")
        w.add("sub","f2")
        w.add("pow","f3")
        w.add("pow","f4")
        w.add("add","f5")
        # f1 = src_a + src_b
        w.connect("src_a","f1:a")
        w.connect("src_b","f1:b")
        # f2 = src_b - src_a
        w.connect("src_b","f2:a")
        w.connect("src_a","f2:b")
        # f3 = f1^2
        w.connect("f1","f3:a")
        w.connect("src_p","f3:b")
        # f4 = f2^2
        w.connect("f2","f4:a")
        w.connect("src_p","f4:b")
        # f5 = f4 + f3
        w.connect("f3","f5:a")
        w.connect("f4","f5:b")
        print ""
        w.execute()
        act_res = w.registry_fetch("f5")
        # get output and test
        test_res = npy.power((v_a + v_b),2.0)+ npy.power((v_a - v_b),2.0)
        dsum = npy.sum(act_res - test_res)
        print "Filter Graph Result: %s" % str(act_res)
        print "Test Result:         %s" % str(test_res)
        print "Difference:          %s" % str(dsum)
        self.assertTrue(dsum < 1e-6)
    def test_02_direct_reg_access(self):
        w = Workspace()
        w.register_filters(npy_ops)
        v_a = npy.array(range(10),dtype=npy.double)
        v_b = npy.array(range(10),dtype=npy.double)
        w.registry_add("src_a",v_a)
        w.registry_add("src_b",v_b)
        w.add("add","f1")
        w.add("sub","f2")
        w.add("mult","f3")
        w.add("mult","f4")
        w.add("add","f5")
        # f1 = src_a + src_b
        w.connect(":src_a","f1:a")
        w.connect(":src_b","f1:b")
        # f2 = src_b - src_a
        w.connect(":src_b","f2:a")
        w.connect(":src_a","f2:b")
        # f3 = f1^2
        w.connect("f1","f3:a")
        w.connect("f1","f3:b")
        # f4 = f2^2
        w.connect("f2","f4:a")
        w.connect("f2","f4:b")
        # f5 = f4 + f3
        w.connect("f3","f5:a")
        w.connect("f4","f5:b")
        print ""
        w.execute()
        act_res = w.registry_fetch("f5")
        # get output and test
        test_res = npy.power((v_a + v_b),2.0)+ npy.power((v_a - v_b),2.0)
        dsum = npy.sum(act_res - test_res)
        print "Filter Graph Result: %s" % str(act_res)
        print "Test Result:         %s" % str(test_res)
        print "Difference:          %s" % str(dsum)
        self.assertTrue(dsum < 1e-6)


if __name__ == '__main__':
    unittest.main()

