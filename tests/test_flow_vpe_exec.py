#!/usr/bin/env python
#
# ${disclaimer}
#
"""
 file: test_flow_vpe_exec.py
 author: Cyrus Harrison <cyrush@llnl.gov>
 created: 1/04/2012
 description:
    TODO

"""


import unittest
import visit
import os

from os.path import join as pjoin

from flow import vpe
from flow.core import *
from flow.filters import npy_ops


class TestFlowVPE(unittest.TestCase):
    def setUp(self):
        # open test dataset
        self.data_path = pjoin("tests","data","rect2d.silo")
        visit.OpenDatabase(self.data_path)
    def test_flow_expr_ex1(self):
        vpe.define_flow_expr("flow",file="examples/flow.setup.example.1.py")
        visit.AddPlot("Pseudocolor","flow")
        # the flow kernel should calc d+p
        # define another expression to check the actual result.
        visit.DefineScalarExpression("check","flow - (d+p)")
        visit.AddPlot("Pseudocolor","check")
        visit.DrawPlots()
        # the total sum of all scalar vals of 'check' should equal zero.
        res = 1e8
        if visit.Query("Variable Sum"):
            res = visit.GetQueryOutputValue()
        self.assertTrue(res < 1.0e-8)
    def test_flow_expr_ex2(self):
        vpe.define_flow_expr("flow",file="examples/flow.setup.example.2.py")
        visit.AddPlot("Pseudocolor","flow")
        # the flow kernel should calc d+p
        # define another expression to check the actual result.
        visit.DefineScalarExpression("check","flow - ((d + p)^2.0 + (d-p)^2.0)")
        visit.AddPlot("Pseudocolor","check")
        visit.DrawPlots()
        # the total sum of all scalar vals of 'check' should equal zero.
        res = 1e8
        if visit.Query("Variable Sum"):
            res = visit.GetQueryOutputValue()
        self.assertTrue(res < 1.0e-8)
    def tearDown(self):
        # clean up
        visit.DeleteAllPlots()
        visit.CloseDatabase(self.data_path)
        visit.CloseComputeEngine()
        
