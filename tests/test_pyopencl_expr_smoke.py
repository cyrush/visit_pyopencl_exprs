#!/usr/bin/env python
#
# ${disclaimer}
#
"""
 file: test_pyopencl_smoke_expr.py
 author: Cyrus Harrison <cyrush@llnl.gov>
 created: 12/09/2011
 description:
   A smoke test which checks that everything is in place 
   to use pyopencl within a VisIt python expression.

"""

import unittest
import visit
import os

from os.path import join as pjoin

class TestSmoke(unittest.TestCase):
    def setUp(self):
        # open test dataset
        self.data_path = pjoin("tests","data","rect2d.silo")
        visit.OpenDatabase(self.data_path)
    def test_smoke_expr(self):
        # define our python expression
        visit.DefinePythonExpression("smoke",
                                     file=pjoin("tests","pyopencl_smoke_expr.vpe"),
                                     args=["d","p"])
        # the OpenCL kernel should calc d+p
        # define another expression to check the actual result.
        visit.DefineScalarExpression("check","smoke - (d+p)")
        visit.AddPlot("Pseudocolor","check")
        visit.DrawPlots()
        # the total sum of all scalar vals of 'check' should equal zero.
        visit.Query("Variable Sum")
        res = visit.GetQueryOutputValue()
        self.assertTrue(res < 1.0e-8)
    def tearDown(self):
        # clean up
        visit.DeleteAllPlots()
        visit.CloseDatabase(self.data_path)
        visit.CloseComputeEngine()
        
