#!/usr/bin/env python
#
# ${disclaimer}
#
"""
 file: single_node_scale.py
 author: Cyrus Harrison <cyrush@llnl.gov>
 description:
  TODO

"""

import sys
import subprocess
import socket
import os
from os.path import join as pjoin

def ser(rtype,base_path,plat,dev):
    for cs  in range(1,13):
        cmd  = "python run_timings.py "
        dbfile = "rt3d_export_center_with_coords_col_%04d_chunk_size_%03d_idx_0000.vtk " % (cs-1,cs)
        dbfile = pjoin(base_path,dbfile)
        cmd += " %s %s %d %d %s 7  1 _ser_test_chunk_size_%03d " % (rtype,dbfile,plat,dev,method,cs)
        subprocess.call(cmd,shell=True)

def main():
    run_par = False
    args       = sys.argv
    base_path  = args[1]
    plat       = int(args[2])
    dev        = int(args[3])
    if len(args) == 4:
        runs = ["mag","vort","q"]
    else:
        runs = [ a for a in args[4:] if not a.startswith("--")]
    for run in runs:
        ser(run,base_path,plat,dev)

if __name__ == "__main__":
    main()


