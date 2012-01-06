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
import re
from ..core import Workspace

from os.path import join as pjoin

def vpe_path():
    return os.path.split(os.path.abspath(__file__))[0]

def escape_src(src):
    # make sure the source will survive visits expr parser
    src = src.replace('"','\\"')
    src = src.replace('\n','\\n')
    src = src.replace(' ','\\s')
    return src

def define_flow_expr(ename,src=None,file=None):
    # get proper vpe path ...
    fvpe = pjoin(vpe_path(),"visit_flow_exec.vpe")
    args = []
    script_src = src
    if script_src is None and not file is None:
        # we want to pass workspace script as a source
        # string, b/c the engine may not mount the same fs.
        script_src = open(file).read()
    w = Workspace.load_workspace_script(src=script_src)
    # get root vars & use as expr args
    evars = w.registry_sources()
    args.extend(evars)
    script_src = escape_src(script_src)
    args.extend(['"src"','"' + script_src + '"'])
    visit.DefinePythonExpression(ename,file=fvpe,args=args)
