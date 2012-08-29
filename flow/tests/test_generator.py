#!/usr/bin/env python
#
# ${disclaimer}
#
"""
 file: test_parser.py
 author: Cyrus Harrison <cyrush@llnl.gov>
 created: 8/29/2012
 description:
    unittest test cases for parser front-end.

"""

import unittest
try:
    import numpy as npy
except:
    pass

from flow import *
from flow.filters import npy_ops

from decorators import numpy_test
# uncomment for detailed exe info
#import logging
#logging.basicConfig(level=logging.INFO)

class TestParser(unittest.TestCase):
    def test_01_simple_expr_gen(self):
        filters = Generator.parse_network("vel_mag = sqrt(vx^2 + vy^2 + vz^2)")
        print ""
        for f in filters:
            print f
        self.assertTrue(True)
    def test_02_simple_expr_gen_context(self):
        w = Workspace()
        w.register_filters(npy_ops)
        v_a = npy.array(range(10),dtype=npy.double)
        v_b = npy.array(range(10),dtype=npy.double)
        c_2 = 2.0
        w.registry_add(":v_a",v_a)
        w.registry_add(":v_b",v_b)
        w.registry_add(":c_2",c_2)
        print ""
        expr = "res = (v_a + v_b)^c_2 + (v_a  - v_b)^c_2"
        print "test_expr: " + expr
        filters = Generator.parse_network(expr,w)
        print ""
        print w.graph
        print w.execution_plan()
        act_res = w.execute()
        # get output and test
        test_res = npy.power((v_a + v_b),2.0)+ npy.power((v_a - v_b),2.0)
        dsum = npy.sum(act_res - test_res)
        print "Filter Graph Result: %s" % str(act_res)
        print "Test Result:         %s" % str(test_res)
        print "Difference:          %s" % str(dsum)
        self.assertTrue(dsum < 1e-6)

if __name__ == '__main__':
    unittest.main()

