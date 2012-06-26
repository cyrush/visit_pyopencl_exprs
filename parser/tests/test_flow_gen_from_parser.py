#!/usr/bin/env python
#
# ${disclaimer}
#
"""
 file: test_flow_gen_from_parser.py
 author: Maysam Moussalem <maysam@cs.utexas.edu>
 created: 05/29/2012
 description:
    Unittest test cases for flow generation from parsed expressions.

"""

import unittest
try:
    import numpy as npy
except:
    pass

from flow_gen_from_parser import *

# uncomment for detailed exe info
#import logging
#logging.basicConfig(level=logging.INFO)


class TestVisItExprParserPrec(unittest.TestCase):
    def setUp(self):
        print ""

    def test_simple_flow_01(self):
        """ Test data source addition. """
        flow_gen_output = add_data_source("x")
        expected_solution = "    ctx.registry_add(\":x\",v_x)\n"
        self.assertEqual(flow_gen_output, expected_solution, "Test 01 failed.")

    def test_simple_flow_02(self):
        """ Test filter addition. """
        flow_gen_output = add_filter("add", "f0")
        expected_solution = "    ctx.add_filter(\"add\", \"f0\")\n"
        self.assertEqual(flow_gen_output, expected_solution, "Test 02 failed.")

    def test_simple_flow_03(self):
        """ Test decomposition filter addition. """ 
        flow_gen_output = add_decompose_filter("decompose", "f0", 0)
        expected_solution = "    ctx.add_filter(\"decompose\", \"f0\", {\"index\":0})\n"
        self.assertEqual(flow_gen_output, expected_solution, "Test 03 failed.")

    def test_simple_flow_04(self):
        """ Test connection of database variable to filter. """
        flow_gen_output = connect_filter_var("x", 1, "f0")
        expected_solution = "    ctx.connect(\":x\",(\"f0\",1))\n"
        self.assertEqual(flow_gen_output, expected_solution, "Test 04 failed.")

    def test_simple_flow_05(self):
        """ Test connection of constant value to filter. """
        flow_gen_output = connect_filter("123", 0, "f0")
        expected_solution = "    ctx.connect(\"123\",(\"f0\",0))\n"
        self.assertEqual(flow_gen_output, expected_solution, "Test 05 failed.")

    def test_simple_flow_06(self):
        """ Test connection of one filter's output to another filter. """
        flow_gen_output = connect_filter("f0", 0, "f1")
        expected_solution = "    ctx.connect(\"f0\",(\"f1\",0))\n"
        self.assertEqual(flow_gen_output, expected_solution, "Test 06 failed.")

    def test_simple_flow_07(self):
        """ Test flow creation for simple expression (no nested expressions as arguments)
        with one argument. """
        flow_gen_input = "cos(x)"
        flow_gen_output = get_flow_code(flow_gen_input)
        expected_solution = "    ctx.add_filter(\"cos\", \"f1\")\n"
        expected_solution += "    ctx.connect(\":x\",(\"f1\",0))\n"
        self.assertEqual(flow_gen_output, expected_solution, "Test 07 failed.")

    def test_simple_flow_08(self):
        """ Test flow creation for simple expression with several arguments. """
        flow_gen_input = "a + b"
        flow_gen_output = get_flow_code(flow_gen_input)
        expected_solution = "    ctx.add_filter(\"+\", \"f1\")\n"
        expected_solution += "    ctx.connect(\":a\",(\"f1\",0))\n"
        expected_solution += "    ctx.connect(\":b\",(\"f1\",1))\n"
        self.assertEqual(flow_gen_output, expected_solution, "Test 08 failed.")

    def test_simple_flow_09(self):
        """ Test flow creation for expression with a nested argument. """
        flow_gen_input = "(a + b) + c"
        flow_gen_output = get_flow_code(flow_gen_input)
        expected_solution = "    ctx.add_filter(\"+\", \"f1\")\n"
        expected_solution += "    ctx.add_filter(\"+\", \"f2\")\n"
        expected_solution += "    ctx.connect(\":a\",(\"f2\",0))\n"
        expected_solution += "    ctx.connect(\":b\",(\"f2\",1))\n"
        expected_solution += "    ctx.connect(\"f2\",(\"f1\",0))\n"
        expected_solution += "    ctx.connect(\":c\",(\"f1\",1))\n"
        self.assertEqual(flow_gen_output, expected_solution, "Test 09 failed.")

    def test_simple_flow_10(self):
        """ Test flow creation for expression with several nested arguments. """
        flow_gen_input = "(a + b) * (c + d)"
        flow_gen_output = get_flow_code(flow_gen_input)
        expected_solution = "    ctx.add_filter(\"*\", \"f1\")\n"
        expected_solution += "    ctx.add_filter(\"+\", \"f2\")\n"
        expected_solution += "    ctx.connect(\":a\",(\"f2\",0))\n"
        expected_solution += "    ctx.connect(\":b\",(\"f2\",1))\n"
        expected_solution += "    ctx.connect(\"f2\",(\"f1\",0))\n"
        expected_solution += "    ctx.add_filter(\"+\", \"f3\")\n"
        expected_solution += "    ctx.connect(\":c\",(\"f3\",0))\n"
        expected_solution += "    ctx.connect(\":d\",(\"f3\",1))\n"
        expected_solution += "    ctx.connect(\"f3\",(\"f1\",1))\n"
        self.assertEqual(flow_gen_output, expected_solution, "Test 10 failed.")

    def test_simple_flow_11(self):
        """ Test flow creation in case of assignment. """
        flow_gen_input = "a = cos(x)"
        flow_gen_output = get_flow_code(flow_gen_input)
        expected_solution = "    ctx.add_filter(\"cos\", \"a\")\n"
        expected_solution += "    ctx.connect(\":x\",(\"a\",0))\n"
        self.assertEqual(flow_gen_output, expected_solution, "Test 11 failed.")

    def test_simple_flow_12(self):
        """ Test flow creation in case of decomposition. """
        flow_gen_input = "cos(x)[0]"
        flow_gen_output = get_flow_code(flow_gen_input)
        expected_solution = "    ctx.add_filter(\"decompose\", \"f1\", {\"index\":0})\n"
        expected_solution += "    ctx.add_filter(\"cos\", \"f2\")\n"
        expected_solution += "    ctx.connect(\":x\",(\"f2\",0))\n"
        expected_solution += "    ctx.connect(\"f2\",(\"f1\",0))\n"
        self.assertEqual(flow_gen_output, expected_solution, "Test 12 failed.")

if __name__ == '__main__':
    unittest.main()

