#!/usr/bin/env python
#
# ${disclaimer}
#
"""
 file: test_workspace.py
 author: Cyrus Harrison <cyrush@llnl.gov>
 created: 3/28/2012
 description:
    unittest test cases for filter workspace setup.

"""

import unittest
import math
from flow import *

# uncomment for detailed exe info
#import logging
#logging.basicConfig(level=logging.INFO)


class CalcPower(Filter):
    filter_type    = "pow"
    input_ports    = ["in"]
    default_params = {"power":2.0}
    output_port    = True
    def execute(self):
        v = self.input("in") 
        return math.pow(v,self.params.power) 
    
class CalcAdd(Filter):
    filter_type    = "add"
    input_ports    = ["in_a","in_b"]
    default_params = {}
    output_port    = True
    def execute(self):
        a = self.input(0) 
        b = self.input(1) 
        return a + b

class CalcContext(Context):
    context_type = "calc"
    def calc_setup(self):
        pass


class TestWorkspace(unittest.TestCase):
    def setUp(self):
        w = Workspace()
        w.register_filter(CalcPower)
        w.register_filter(CalcAdd)
        w.register_context(CalcContext)
        self.w = w
        print ""
    def test_01_simple_setup(self):
        ctx = self.w.add_context("calc","root")
        ctx.calc_setup() # check if we get proper context
        ctx.add_registry_source(":src_a",10.0)
        ctx.add_registry_source(":src_b",20.0)
        self.assertEqual([":src_a",":src_b"],ctx.registry_keys())
        ctx.add_filter("add","f1")
        f2 = ctx.add_filter("pow","f2")
        ctx.connect(":src_a","f1:in_a")
        ctx.connect(":src_b","f1:in_b")
        ctx.connect("f1","f2:in")
        r = self.w.execute()
        self.assertEqual(r,math.pow(10.0+20.0,2.0))
        f2["power"] = 3.0
        r = self.w.execute()
        self.assertEqual(r,math.pow(10.0+20.0,3.0))
        

if __name__ == '__main__':
    unittest.main()

