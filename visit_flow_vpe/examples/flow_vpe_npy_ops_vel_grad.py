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
from flow.filters import npy_ops


def setup_workspace():
    w = Workspace()
    w.register_filters(npy_ops)
    w.add_filter("compose","coord_comp_1")
    w.add_filter("compose","coord_comp_2")
    w.add_filter("compose","vgt_comp_1")
    w.add_filter("compose","vgt_comp_2")
    w.add_filter("decompose","dvxdx",{"index":0})
    w.add_filter("grad","dvx")
    w.connect(":x","coord_comp_1:in_a")
    w.connect(":y","coord_comp_1:in_b")
    w.connect("coord_comp_1","coord_comp_2:in_a")
    w.connect(":z","coord_comp_2:in_b")
    w.connect("coord_comp_2","dvx:coords")
    w.connect(":dims","dvx:dims")
    w.connect(":vx","dvx:in")
    w.connect("dvx","dvxdx:in")
    return w

