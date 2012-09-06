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

def par(rtype,base_path,plat,dev):
    hname = socket.gethostname()
    if hname.count("edge") > 0:
        method = "srun"
    else:
        method = "mpirun"
    for cs  in range(1,2):
        cmd    = "python run_timings.py "
        dbfile =  "rt3d_export_center_chunk_size_%03d.visit " % (cs)
        dbfile = pjoin(base_path,dbfile)
        cmd += " %s %s %d %d %s 5  1 _ser_test_chunk_size_%03d 1" % (rtype,dbfile,plat,dev,method,cs)
        subprocess.call(cmd,shell=True)

def ser(rtype,base_path,plat,dev):
    hname = socket.gethostname()
    if hname.count("edge") > 0:
        method = "srun"
    else:
        method = "mpirun"
    for cs  in range(1,2):
        cmd  = "python run_timings.py "
        dbfile = "rt3d_export_center_with_coords_col_%04d_chunk_size_%03d_idx_0000.vtk " % (cs-1,cs)
        dbfile = pjoin(base_path,dbfile)
        cmd += " %s %s %d %d %s 5  1 _ser_test_chunk_size_%03d " % (rtype,dbfile,plat,dev,method,cs)
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
    if "--par" in args[1:]:
        run_par = True
    for run in runs:
        ser(run,base_path,plat,dev)
        if run_par:
            par(run,base_path,plat,dev)

if __name__ == "__main__":
    main()


