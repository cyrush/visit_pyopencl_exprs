
import subprocess

def par(rtype):
    for cs  in range(1,11):
        cmd  = "python run_timings.py "
        cmd += "/p/lscratchc/cyrush/rt3d_export_center_chunk_size_%03d.visit " % (cs)
        cmd += "%s 10  2 _par_test_chunk_size_%03d " % (rtype,cs)
        subprocess.call(cmd,shell=True)

def ser(rtype):
    for cs  in range(1,11):
        cmd  = "python run_timings.py "
        cmd += "/p/lscratchc/cyrush/rt3d_export/rt3d_export_center_with_coords_col_%04d_chunk_size_%03d_idx_0000.vtk " % (cs-1,cs)
        cmd += "%s 10  1 _ser_test_chunk_size_%03d " % (rtype,cs)
        subprocess.call(cmd,shell=True)

if __name__ == "__main__":
    ser("mag")
    par("mag")
    ser("vort")
    par("vort")
    ser("q")
    par("q")

