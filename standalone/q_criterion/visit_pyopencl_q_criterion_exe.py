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

def exe_3d(db):
    OpenDatabase(db)
    fvpe = "visit_pyopencl_q_criterion.vpe"
    DefinePythonExpression("q_crit",
                            source="PythonFilter.load('%s')\n" % fvpe,
                            args=["x","y","z","vx","vy","vz"])
    AddPlot("Pseudocolor","q_crit")
    DrawPlots()

def main():
    exe_3d("../../rt3d_small_chunk.silo")


if __visit_script_file__ == __visit_source_file__:
    main()


