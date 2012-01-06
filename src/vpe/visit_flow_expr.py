#!/usr/bin/env python
#
# ${disclaimer}
#
"""
 file: visit_flow_expr.py
 author: Cyrus Harrison <cyrush@llnl.gov>
 created: 12/09/2011
 description:
    TODO

"""
import visit
import os
import pickle

from os.path import join as pjoin

def vpe_path():
    return os.path.split(os.path.abspath(__file__))[0]

def define_flow_expr(ename,evars,wfile):
    # get proper vpe path ...
    fvpe = pjoin(vpe_path(),"visit_flow_exec.vpe")
    args = []
    args.extend(evars)
    args.append('"' + wfile + '"')
    visit.DefinePythonExpression(ename,file=fvpe,args=args)
