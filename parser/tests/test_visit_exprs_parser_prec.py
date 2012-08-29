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

    def test_simple_expr_01(self):
        """ Simple test for constants. """
        expr = "123"
        parser_solution = str(parse(expr))
        expected_solution = "(const(123), {})"
        self.assertEqual(parser_solution, expected_solution, "Test 01 failed on expr.")

    def test_simple_expr_02(self):
        """ Simple test for variables. """
        expr = "a"
        parser_solution = str(parse(expr))
        expected_solution = "(a, {})"
        self.assertEqual(parser_solution, expected_solution, "Test 02 failed on expr.")

    def test_simple_expr_03(self):
        """ Simple test for binary math operation. """
        expr = "a + b"
        parser_solution = str(parse(expr))
        expected_solution = "(<FuncCallObj>+([a, b]), {})"
        self.assertEqual(parser_solution, expected_solution, "Test 03 failed on expr.")

    def test_simple_expr_04(self):
        """ Simple test for unary math operation. """
        expr = "cos(x)"
        parser_solution = str(parse(expr))
        expected_solution = "(<FuncCallObj>cos([x]), {})"
        self.assertEqual(parser_solution, expected_solution, "Test 04 failed on expr.")

    def test_simple_expr_05(self):
        """ Simple test for assignment. """
        expr = "a = b"
        parser_solution = str(parse(expr))
        expected_solution = "(b, {a: b})"
        self.assertEqual(parser_solution, expected_solution, "Test 05 failed on expr.")

    def test_simple_expr_06(self):
        """ Test expression assignment."""
        expr = "a = (b + c)"
        parser_solution = str(parse(expr))
        expected_solution = "(<FuncCallObj>+([b, c]), {a: <FuncCallObj>+([b, c])})"
        self.assertEqual(parser_solution, expected_solution, "Test 06 failed on expr.")

    def test_simple_expr_07(self):
        """ Simple test for relational operations. """
        expr = "a < b"
        parser_solution = str(parse(expr))
        expected_solution = "(<FuncCallObj><([a, b]), {})"
        self.assertEqual(parser_solution, expected_solution, "Test 07 failed on expr.")

    def test_simple_expr_08(self):
        """ Simple test for decomposition. """
        expr = "cos(x)[0]"
        parser_solution = str(parse(expr))
        expected_solution = "(<FuncCallObj>decompose([<FuncCallObj>cos([x]), const(0)]), {})"
        self.assertEqual(parser_solution, expected_solution, "Test 08 failed on expr.")

    def test_simple_expr_09(self):
        """ Test precedence. """
        expr = "a + b + c"
        parser_solution = str(parse(expr))
        expected_solution = "(<FuncCallObj>+([<FuncCallObj>+([a, b]), c]), {})"
        self.assertEqual(parser_solution, expected_solution, "Test 09 failed on expr.")

    def test_simple_expr_10(self):
        """ Test precendence enforced with brackets. """
        expr = "a + (b + c)"
        parser_solution = str(parse(expr))
        expected_solution = "(<FuncCallObj>+([a, <FuncCallObj>+([b, c])]), {})"
        self.assertEqual(parser_solution, expected_solution, "Test 10 failed on expr.")

    def test_simple_expr_11(self):
        """ Test precendence order. """
        expr = "a + b * c"
        parser_solution = str(parse(expr))
        expected_solution = "(<FuncCallObj>+([a, <FuncCallObj>*([b, c])]), {})"
        self.assertEqual(parser_solution, expected_solution, "Test 11 failed on expr.")

    def test_simple_expr_12(self):
        """ Test more complex assignment operation. """
        expr = "a = (cos (x) + sin(y))"
        parser_solution = str(parse(expr))
        expected_solution = "(<FuncCallObj>+([<FuncCallObj>cos([x]), <FuncCallObj>sin([y])]), {a: <FuncCallObj>+([<FuncCallObj>cos([x]), <FuncCallObj>sin([y])])})"
        self.assertEqual(parser_solution, expected_solution, "Test 12 failed on expr.")


if __name__ == '__main__':
    unittest.main()

