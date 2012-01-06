#!/usr/bin/env python
#
# ${disclaimer}
#
"""
 file: flow.setup.example.1.py
 author: Cyrus Harrison <cyrush@llnl.gov>
 created: 1/5/2012
 description:
   TODO

"""
from flow.core import *
from flow.filters import npy_ops

def setup_workspace():
    w = Workspace()
    w.register_filters(npy_ops)
    w.add("add","filter_1")
    # The ':' prefix allows access a scalar value from the input dataset
    # this example sets up a simple filter that adds executes:
    # d + p
    w.connect(":d","filter_1:a")
    w.connect(":p","filter_1:b")
    return w