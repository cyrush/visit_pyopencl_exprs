#!/usr/bin/env python
#
# ${disclaimer}
#
"""
 file: test_interactive.py
 author: Cyrus Harrison <cyrush@llnl.gov>
 created: 12/09/2011
 description:
    TODO

"""

import unittest
import numpy as npy

from flow.core import *
from flow.interactive import *
from flow.filters import npy_ops

class TestInteractive(unittest.TestCase):
    def test_01_simple_interactive_workspace(self):
        w = Workspace()
        w.register_filters(npy_ops)
        set_workspace(w)
        v_a = npy.array(range(10),dtype=npy.double)
        v_b = npy.array(range(10),dtype=npy.double)
        add("src","src_a",{"data":v_a})
        add("src","src_b",{"data":v_b})
        add("add","fadd")
        connect("src_a","fadd:a")
        connect("src_b","fadd:b")
        print ""
        execute()
        act_res = registry_fetch("fadd")
        # get output and test
        test_res = v_a + v_b
        dsum = npy.sum(act_res - test_res)
        print "Filter Graph Result: %s" % str(act_res)
        print "Test Result:         %s" % str(test_res)
        print "Difference:          %s" % str(dsum)
        self.assertTrue(dsum < 1e-6)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()

