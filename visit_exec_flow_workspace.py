# [Visit Python Script]
#
#
# ${disclaimer}
#
"""
 file: visit_exec_flow_workspace.py
 author: Cyrus Harrison <cyrush@llnl.gov>
 created: 1/04/2012
 description:
   Driver script that executes a flow workspace on 'rect2d.silo'.

"""

import os
import visit
from os.path import join as pjoin
from flow import vpe

def main():
    args = Argv()
    wfile = args[-1]
    vars  = args[:-1]
    visit.OpenDatabase(pjoin("tests","data","rect2d.silo"))
    vpe.define_flow_expr("flow",vars,wfile)
    visit.AddPlot("Pseudocolor","flow")
    visit.DrawPlots()

if __visit_script_file__ == __visit_source_file__:
    main()