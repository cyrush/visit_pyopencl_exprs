
import sys
import subprocess
import socket


def par(rtype,base_path):
    hname = socket.gethostname()
    if hname.count("edge") > 0:
        method = "srun"
    else:
        method = "mpirun"
    for cs  in range(1,11):
        cmd  = "python run_timings.py %s " % method
        rf  =  "rt3d_export_center_chunk_size_%03d.visit " % (cs)
        cmd +=  pjoin(base_path,rf)
        cmd += " %s 10  2 _par_test_chunk_size_%03d " % (rtype,cs)
        subprocess.call(cmd,shell=True)

def ser(rtype,base_path):
    hname = socket.gethostname()
    if hname.count("edge") > 0:
        method = "srun"
    else:
        method = "mpirun"
    for cs  in range(1,11):
        cmd  = "python run_timings.py %s " % method
        rf   = "rt3d_export_center_with_coords_col_%04d_chunk_size_%03d_idx_0000.vtk " % (cs-1,cs)
        cmd += pjoin(base_path,rf)
        cmd += " %s 10  1 _ser_test_chunk_size_%03d " % (rtype,cs)
        subprocess.call(cmd,shell=True)

def main():
    run_par = False
    args = sys.argv
    base_path  = args[1]
    if len(args) == 2:
        runs = ["mag","vort","q"]
    else:
        runs = [ a for a in args[2:] if not a.startswith("--")]
    if "--par" in args[1:]:
        run_par = True
    for run in runs:
        ser(run)
        if run_par:
            par(run)

if __name__ == "__main__":
    main()

