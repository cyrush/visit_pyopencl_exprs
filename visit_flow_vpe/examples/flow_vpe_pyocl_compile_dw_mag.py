#!/usr/bin/env python
#
# ${disclaimer}
#
"""
 file: vpe_flow_npy_ops_example_1.py
 author: Cyrus Harrison <cyrush@llnl.gov>
 created: 3/28/2012
 description:
    vpe flow example demonstrating use of flow.filters.npy_ops.

"""


from flow import *
from flow.filters import pyocl_compile


def setup_workspace():
    w = Workspace()
    w.register_filters(pyocl_compile)
    ctx = w.add_context("pyocl_compile","root")
    ctx.start()
    ctx.add_filter("decompose","dwdx",{"index":0})
    ctx.add_filter("decompose","dwdy",{"index":1})
    ctx.add_filter("decompose","dwdz",{"index":2})
    ctx.add_filter("grad","dw")
    ctx.add_filter("mult","vx_sq")
    ctx.add_filter("mult","vy_sq")
    ctx.add_filter("mult","vz_sq")
    ctx.add_filter("add","v_add_1")
    ctx.add_filter("add","v_add")
    ctx.add_filter("sqrt","v_sqrt")
    ctx.connect(":vz","dw:in")
    ctx.connect(":dims","dw:dims")
    ctx.connect(":x","dw:x")
    ctx.connect(":y","dw:y")
    ctx.connect(":z","dw:z")
    ctx.connect("dw","dwdx:in")
    ctx.connect("dw","dwdy:in")
    ctx.connect("dw","dwdz:in")
    ctx.connect("dwdx","vx_sq:in_a")
    ctx.connect("dwdx","vx_sq:in_b")
    ctx.connect("dwdy","vy_sq:in_a")
    ctx.connect("dwdy","vy_sq:in_b")
    ctx.connect("dwdz","vz_sq:in_a")
    ctx.connect("dwdz","vz_sq:in_b")
    ctx.connect("vx_sq","v_add_1:in_a")
    ctx.connect("vy_sq","v_add_1:in_b")
    ctx.connect("v_add_1","v_add:in_a")
    ctx.connect("vz_sq","v_add:in_b")
    ctx.connect("v_add","v_sqrt:in")
    print str(w.execution_plan())
    return w


