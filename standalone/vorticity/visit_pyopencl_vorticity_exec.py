#!/usr/bin/env python
#
# ${disclaimer}
#
"""
 file: visit_pyopencl_grad_exec.py
 author: Cyrus Harrison <cyrush@llnl.gov>
 created: 2/17/2012
 description:
    TODO

"""
import visit
import time
def exe_3d(db):
    OpenDatabase(db)
    fvpe = "visit_pyopencl_vorticity.vpe"
    DefinePythonExpression("vort_mag",
                            source="PythonFilter.load('%s')\n" % fvpe,
                            args=["x","y","z","vx","vy","vz"])
    AddPlot("Pseudocolor","vort_mag")
    start = time.time()
    DrawPlots()
    stop  = time.time()
    print "DrawPlots time = ", str((stop - start))


def main(db):
    exe_3d(db)


if __visit_script_file__ == __visit_source_file__:
    args = Argv()
    db = "../../rt3d_one_chunk.silo"
    if len(args) > 0:
        db = args[0]
    main(db)


