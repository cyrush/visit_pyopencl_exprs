#!/usr/bin/env python
#
# ${disclaimer}
#
"""
 file: interactive.py
 author: Cyrus Harrison <cyrush@llnl.gov>
 created: 10/14/2010
 description:
    TODO

"""

import sys
import traceback

from ..core.workspace import *
from ..core.registry import *
from ..core.filter_graph import *

__workspace = None

def __ehook(type, value, tback):
    traceback.print_tb(tback)
    print 'Error:', value.__class__.__name__
    print "Message:"
    tok = str(value).split("\n")
    for t in tok:
        print " %s" % t

def trap_exceptions():
    sys.excepthook = __ehook

def set_workspace(w):
    global __workspace
    __workspace = w

def workspace():
    global __workspace
    if __workspace is None:
        __workspace = Workspace()
    return __workspace

def add(filter_type,name = None, props= None):
    return workspace().add(filter_type,name,props)

def remove(filter_name):
    return workspace().remove(filter_name)

def connect(src_name,*des_filters):
    return workspace().connect(src_name,*des_filters)

def execute():
    return workspace().execute()

def registry_add(key,obj,uref=-1):
    return workspace().registry_add(key,obj,uref=-1)

def registry_fetch(node_name):
    return workspace().registry_fetch(node_name)

def registry_clear():
    return workspace().registry_clear()

__all__ = ["trap_exceptions",
           "set_workspace",
           "workspace",
           "add",
           "remove",
           "connect",
           "execute",
           "registry_fetch"]

