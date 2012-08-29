
import sys
import subprocess
import socket


def par(rtype):
    hname = socket.gethostname()
    if hname.count("edge") > 0:
        base   = "/p/lscratchc/cyrush/"
        method = "srun"
    else: # assume longhorn
        base = "/scratch/01937/cyrush/data/"
        method = "mpirun"
    for cs  in range(1,11):
        cmd  = "python run_timings.py %s " % method
        cmd += base + "rt3d_export_center_chunk_size_%03d.visit " % (cs)
        cmd += "%s 10  2 _par_test_chunk_size_%03d " % (rtype,cs)
        subprocess.call(cmd,shell=True)

def ser(rtype):
    hname = socket.gethostname()
    if hname.count("edge") > 0:
        base = "/p/lscratchc/cyrush/rt3d_export/"
        method = "srun"
    else: # assume longhorn
        base = "/scratch/01937/cyrush/data/rt3d_export/"
        method = "mpirun"
    for cs  in range(1,11):
        cmd  = "python run_timings.py %s " % method
        cmd += base + "rt3d_export_center_with_coords_col_%04d_chunk_size_%03d_idx_0000.vtk " % (cs-1,cs)
        cmd += "%s 10  1 _ser_test_chunk_size_%03d " % (rtype,cs)
        subprocess.call(cmd,shell=True)

def main():
    run_par = False
    args = sys.argv
    if len(args) == 1:
        runs = ["mag","vort","q"]
    else:
        runs = [ a for a in args[1:] if not a.startswith("--")]
    if "--par" in args[1:]:
        run_par = True
    for run in runs:
        ser(run)
        if run_par:
            par(run)

if __name__ == "__main__":
    main()

