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
from visit_flow_vpe import *

def main():
    args   = Argv()
    wfile  = args[0]
    dbfile = pjoin("tests","_data","rect2d.silo")
    if len(args) > 1:
        dbfile = args[1]
    visit.OpenDatabase(dbfile)
    define_flow_vpe("flow",file=wfile)
    visit.AddPlot("Pseudocolor","flow")
    visit.DrawPlots()

if __visit_script_file__ == __visit_source_file__:
    main()
    if "-nowin" in sys.argv:
        sys.exit(0)


