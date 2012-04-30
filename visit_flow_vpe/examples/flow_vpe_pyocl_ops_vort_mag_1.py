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
from flow.filters import pyocl_ops


def setup_workspace():
    w = Workspace()
    w.register_filters(pyocl_ops)
    ctx  = w.add_context("pyocl_ops","root")
    ctx.start()
    ctx.add_filter("decompose","dudx",{"index":0})
    ctx.add_filter("decompose","dudy",{"index":1})
    ctx.add_filter("decompose","dudz",{"index":2})
    ctx.add_filter("decompose","dvdx",{"index":0})
    ctx.add_filter("decompose","dvdy",{"index":1})
    ctx.add_filter("decompose","dvdz",{"index":2})
    ctx.add_filter("decompose","dwdx",{"index":0})
    ctx.add_filter("decompose","dwdy",{"index":1})
    ctx.add_filter("decompose","dwdz",{"index":2})
    ctx.add_filter("grad","du")
    ctx.add_filter("grad","dv")
    ctx.add_filter("grad","dw")
    ctx.add_filter("sub","vort_x")
    ctx.add_filter("sub","vort_y")
    ctx.add_filter("sub","vort_z")
    ctx.add_filter("mult","vort_x_sq")
    ctx.add_filter("mult","vort_y_sq")
    ctx.add_filter("mult","vort_z_sq")
    ctx.add_filter("add","vort_add_1")
    ctx.add_filter("add","vort_add")
    ctx.add_filter("sqrt","vort_sqrt")
    w.connect(":x","du:x")
    w.connect(":y","du:y")
    w.connect(":z","du:z")
    w.connect(":dims","du:dims")
    w.connect(":vx","du:in")
    w.connect(":x","dv:x")
    w.connect(":y","dv:y")
    w.connect(":z","dv:z")
    w.connect(":dims","dv:dims")
    w.connect(":vy","dv:in")
    w.connect(":x","dw:x")
    w.connect(":y","dw:y")
    w.connect(":z","dw:z")
    w.connect(":dims","dw:dims")
    w.connect(":vz","dw:in")
    # w.connect("du","dudx:in")
    w.connect("du","dudy:in")
    w.connect("du","dudz:in")
    w.connect("dv","dvdx:in")
    # w.connect("dv","dvdy:in")
    w.connect("dv","dvdz:in")
    w.connect("dw","dwdx:in")
    w.connect("dw","dwdy:in")
    # w.connect("dw","dwdz:in")
    w.connect("dwdy","vort_x:in_a")
    w.connect("dvdz","vort_x:in_b")
    w.connect("dudz","vort_y:in_a")
    w.connect("dwdx","vort_y:in_b")
    w.connect("dvdx","vort_z:in_a")
    w.connect("dudy","vort_z:in_b")
    w.connect("vort_x","vort_x_sq:in_a")
    w.connect("vort_x","vort_x_sq:in_b")
    w.connect("vort_y","vort_y_sq:in_a")
    w.connect("vort_y","vort_y_sq:in_b")
    w.connect("vort_z","vort_z_sq:in_a")
    w.connect("vort_z","vort_z_sq:in_b")
    w.connect("vort_x_sq","vort_add_1:in_a")
    w.connect("vort_y_sq","vort_add_1:in_b")
    w.connect("vort_add_1","vort_add:in_a")
    w.connect("vort_z_sq","vort_add:in_b")
    w.connect("vort_add","vort_sqrt:in")
    print str(w.execution_plan())
    return w


