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
    fvpe = "visit_pyopencl_vorticity.vpe"
    DefinePythonExpression("vort",
                            source="PythonFilter.load('%s')\n" % fvpe,
                            args=["x","y","z","vx","vy","vz"],type="vector")
    DefineScalarExpression("vort_mag","magnitude(vort)")
    AddPlot("Pseudocolor","vort_mag")
    DrawPlots()

def main():
    exe_3d("../../rt3d_small_chunk.silo")

        
if __visit_script_file__ == __visit_source_file__:
    main()

    
