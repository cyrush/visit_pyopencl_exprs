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

def define_flow_vpe(ename,expr,
                    filter_set,
                    platform_id,
                    device_id):
    # get proper vpe path ...
    fvpe = pjoin(vpe_path(),"visit_flow_exec.vpe")
    args = []
    # keep a path for the old way
    if expr.endswith(".py") and os.path.isfile(expr):
        filter_set = "src"
        expr = open(expr).read()
        w = Workspace.load_workspace_script(src=expr)
    else:
        if os.path.isfile(expr):
            expr = open(expr).read()
        w = Workspace()
        w.register_filters(flow.filters.module(filter_set))
        ctx = w.add_context(filter_set,"root")
        w.setup_expression_network(expr,ctx)
    # get root vars & use as expr args
    evars = w.filter_names()
    evars = [ evar[1:] for evar in evars if evar[0] == ":" and evar != ":dims"]
    #print "evars: " , evars
    args.extend(evars)
    expr_escaped = escape_src(expr)
    args.extend(['"'+ filter_set +  '"','"' + expr_escaped+ '"'])
    args.extend(['"%d"' % platform_id, '"%d"' % device_id])
    visit.DefinePythonExpression(ename,file=fvpe,args=args)

def vpe_timing_info(ttag,wcomps,wtot):
    itot  = 0
    ctx_ste = ttag["total"]["ste"]
    ctx_qte = ttag["total"]["qte"]
    ctx_ste_diff = wtot.get_elapsed() - ctx_ste
    ctx_ste_diff_perc = str(round(100.0*ctx_ste_diff/wtot.get_elapsed(),2)) + " (%)"
    ctx_qte_diff = wtot.get_elapsed() - ctx_qte
    ctx_qte_diff_perc = str(round(100.0*ctx_qte_diff/wtot.get_elapsed(),2)) + " (%)"
    print "::TimingInfo "
    for wcomp in wcomps:
        itot += wcomp.get_elapsed()
        print "::TimingInfo  %s" % wcomp
    print "::TimingInfo  %s" % wtot
    print ""
    print "::TimingInfo  wtot - (all_wcomps) = %s" % repr(wtot.get_elapsed() - itot)
    print "::TimingInfo  ctx_ste = %s" % repr(ctx_ste)
    print "::TimingInfo  wtot - ctx_ste = %s" % repr(ctx_ste_diff)
    print "::TimingInfo  ctx_ste_diff/wtot = %s " % ctx_ste_diff_perc
    print ""
    print "::TimingInfo  ctx_qte = %s" % repr(ctx_qte)
    print "::TimingInfo  wtot - ctx_qte = %s" % repr(ctx_qte_diff)
    print "::TimingInfo  ctx_qte_diff/wtot = %s " % ctx_qte_diff_perc

__all__ = [ "define_flow_vpe","vpe_timing_info"]

