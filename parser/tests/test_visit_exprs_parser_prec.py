#!/usr/bin/env python
#
# ${disclaimer}
#
"""
 file: test_visit_exprs_parser_prec.py
 author: Maysam Moussalem <maysam@cs.utexas.edu>
 created: 05/29/2012
 description:
    Unittest test cases for parsed expressions.

"""

import unittest
try:
    import numpy as npy
except:
    pass

from visit_exprs_parser_prec import parse

# uncomment for detailed exe info
#import logging
#logging.basicConfig(level=logging.INFO)


class TestVisItExprParserPrec(unittest.TestCase):
    def setUp(self):
        print ""
    @parser_test
    def test_simple_expr_01(self):
        expr = "a"
        parsed_expr_solution = "a"
        vmaps_solution = {}
        parsed_expr, vmaps = parse(expr)
        self.assertEqual(parsed_expr.name, parsed_expr_solution, "Test 01 failed on expr.")
        self.assertEqual(vmaps_expr, vmaps_solution, "Test 01 failed on vmaps.")

    def test_simple_expr_02(self):
        expr = "a + b"
        parsed_expr_solution = "+([a, b])"
        vmaps_solution = {}
        parsed_expr, vmaps = parse(expr)
        self.assertEqual(parsed_expr.name, parsed_expr_solution, "Test 02 failed on expr.")
        self.assertEqual(vmaps_expr, vmaps_solution, "Test 02 failed on vmaps.")

    def test_simple_expr_03(self):
        expr = "cos(x)"
        parsed_expr_solution = "cos([x])"
        vmaps_solution = {}
        parsed_expr, vmaps = parse(expr)
        self.assertEqual(parsed_expr.name, parsed_expr_solution, "Test 03 failed on expr.")
        self.assertEqual(vmaps_expr, vmaps_solution, "Test 03 failed on vmaps.")

    def test_simple_expr_04(self):
        expr = "a = b"
        parsed_expr_solution = "b"
        vmaps_solution = {a: b}
        parsed_expr, vmaps = parse(expr)
        self.assertEqual(parsed_expr.name, parsed_expr_solution, "Test 04 failed on expr.")
        self.assertEqual(vmaps_expr, vmaps_solution, "Test 04 failed on vmaps.")

    def test_simple_expr_05(self):
        expr = "a = (b + c)"
        parsed_expr_solution = "+([b, c])"
        vmaps_solution = {a: <FuncCallObj>+([b, c])}}
        parsed_expr, vmaps = parse(expr)
        self.assertEqual(parsed_expr.name, parsed_expr_solution, "Test 05 failed on expr.")
        self.assertEqual(vmaps_expr, vmaps_solution, "Test 05 failed on vmaps.")

    def test_simple_expr_06(self):
        expr = "a < b"
        parsed_expr_solution = "<([a, b])"
        vmaps_solution = {}
        parsed_expr, vmaps = parse(expr)
        self.assertEqual(parsed_expr.name, parsed_expr_solution, "Test 06 failed on expr.")
        self.assertEqual(vmaps_expr, vmaps_solution, "Test 06 failed on vmaps.")

    def test_simple_expr_07(self):
        expr = "cos(x)[180]"
        parsed_expr_solution = "decompose([cos([x]), const(180)])"
        vmaps_solution = {}
        parsed_expr, vmaps = parse(expr)
        self.assertEqual(parsed_expr.name, parsed_expr_solution, "Test 07 failed on expr.")
        self.assertEqual(vmaps_expr, vmaps_solution, "Test 07 failed on vmaps.")

    def test_simple_expr_08(self):
        expr = "a + b + c"
        parsed_expr_solution = "+([+([a, b]), c])"
        vmaps_solution = {}
        parsed_expr, vmaps = parse(expr)
        self.assertEqual(parsed_expr.name, parsed_expr_solution, "Test 08 failed on expr.")
        self.assertEqual(vmaps_expr, vmaps_solution, "Test 08 failed on vmaps.")

    def test_simple_expr_09(self):
        expr = "a + b * c"
        parsed_expr_solution = "+([a, *([b, c])])"
        vmaps_solution = {}
        parsed_expr, vmaps = parse(expr)
        self.assertEqual(parsed_expr.name, parsed_expr_solution, "Test 09 failed on expr.")
        self.assertEqual(vmaps_expr, vmaps_solution, "Test 09 failed on vmaps.")

    def test_simple_expr_10(self):
        expr = "a + (b + c)"
        parsed_expr_solution = "+([a, +([b, c])])"
        vmaps_solution = {}
        parsed_expr, vmaps = parse(expr)
        self.assertEqual(parsed_expr.name, parsed_expr_solution, "Test 10 failed on expr.")
        self.assertEqual(vmaps_expr, vmaps_solution, "Test 10 failed on vmaps.")

    def test_simple_expr_11(self):
        expr = "22"
        parsed_expr_solution = "const(22)"
        vmaps_solution = {}
        parsed_expr, vmaps = parse(expr)
        self.assertEqual(parsed_expr.name, parsed_expr_solution, "Test 11 failed on expr.")
        self.assertEqual(vmaps_expr, vmaps_solution, "Test 11 failed on vmaps.")

    def test_simple_expr_12(self):
        expr = "a = cos (x) + sin(y)"
        parsed_expr_solution = "+([cos([x]), sin([y])])"
        vmaps_solution = {a: <FuncCallObj>cos([x])}}
        parsed_expr, vmaps = parse(expr)
        self.assertEqual(parsed_expr.name, parsed_expr_solution, "Test 12 failed on expr.")
        self.assertEqual(vmaps_expr, vmaps_solution, "Test 12 failed on vmaps.")

if __name__ == '__main__':
    unittest.main()

