#
# ${disclaimer}
#
"""
 file: visit_flow_expr.py
 author: Cyrus Harrison <cyrush@llnl.gov>
 created: 12/09/2011
 description:
    Provides a function that defines a VisIt Python Expression
    to execute a flow workspace.

"""

import visit
import os
from flow import *
import flow.filters

from os.path import join as pjoin

def vpe_path():
    return os.path.split(os.path.abspath(__file__))[0]

def escape_src(src):
    # make sure the source will survive visits expr parser
    src = src.replace('"','\\"')
    src = src.replace('\n','\\n')
    src = src.replace(' ','\\s')
    return src

def define_flow_vpe(ename,expr,filter_set="pyocl_ops"):
    # get proper vpe path ...
    fvpe = pjoin(vpe_path(),"visit_flow_exec.vpe")
    args = []
    if os.path.isfile(expr):
        expr = open(expr).read()
    w = Workspace()
    w.register_filters(flow.filters.module(filter_set))
    ctx = w.add_context(filter_set,"root")
    ctx.start()
    w.setup_expression_network(expr,ctx)
    # get root vars & use as expr args
    evars = w.filter_names()
    evars = [ evar[1:] for evar in evars if evar[0] == ":" and evar != ":dims"]
    args.extend(evars)
    expr_escaped = escape_src(expr)
    args.extend(['"'+ filter_set +  '"','"' + expr_escaped+ '"'])
    visit.DefinePythonExpression(ename,file=fvpe,args=args)


__all__ = [ "define_flow_vpe"]

