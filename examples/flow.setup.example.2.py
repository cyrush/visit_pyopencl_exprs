#!/usr/bin/env python
#
# ${disclaimer}
#
"""
 file: flow.setup.example.2.py
 author: Cyrus Harrison <cyrush@llnl.gov>
 created: 1/5/2012
 description:
   TODO

"""

from flow.filters import npy_ops

def setup_workspace(w):
    w.register_filters(npy_ops)
    w.add("add","f1")
    w.add("sub","f2")
    w.add("mult","f3")
    w.add("mult","f4")
    w.add("add","f5")
    # The ':' prefix allows access a scalar value from the input dataset
    # this example sets up a simple filter that adds executes:
    # (d + p)^2 + (d - p)^2
    # f1 = d + p
    w.connect(":d","f1:a")
    w.connect(":p","f1:b")
    # f2 = d - p
    w.connect(":d","f2:a")
    w.connect(":p","f2:b")
    # f3 = f1^2
    w.connect("f1","f3:a")
    w.connect("f1","f3:b")
    # f4 = f2^2
    w.connect("f2","f4:a")
    w.connect("f2","f4:b")
    # f5 = f4 + f3
    w.connect("f3","f5:a")
    w.connect("f4","f5:b")