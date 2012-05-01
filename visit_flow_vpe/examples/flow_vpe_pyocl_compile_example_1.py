#!/usr/bin/env python
#
# ${disclaimer}
#
"""
 file: vpe_flow_pyocl_compile_example_1.py
 author: Cyrus Harrison <cyrush@llnl.gov>
 created: 3/28/2012
 description:
    vpe flow example demonstrating use of flow.filters.pyocl_compile.

"""


from flow import *
from flow.filters import pyocl_compile


def setup_workspace():
    w = Workspace()
    w.register_filters(pyocl_compile)
    ctx  = w.add_context("pyocl_compile","root")
    ctx.start()
    ctx.add_filter("add","f1")
    ctx.add_filter("sub","f2")
    ctx.add_filter("mult","f3")
    ctx.add_filter("mult","f4")
    ctx.add_filter("add","f5")
    # f1 = src_a + src_b
    ctx.connect(":vx","f1:in_a")
    ctx.connect(":vy","f1:in_b")
    # f2 = src_b - src_a
    ctx.connect(":vx","f2:in_a")
    ctx.connect(":vy","f2:in_b")
    # f3 = f1^2
    ctx.connect("f1","f3:in_a")
    ctx.connect("f1","f3:in_b")
    # f4 = f2^2
    ctx.connect("f2","f4:in_a")
    ctx.connect("f2","f4:in_b")
    # f5 = f4 + f3
    ctx.connect("f3","f5:in_a")
    ctx.connect("f4","f5:in_b")
    return w

