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
    DefineVectorExpression("du","gradient(vx)")
    DefineVectorExpression("dv","gradient(vy)")
    DefineVectorExpression("dw","gradient(vz)")
    DefineScalarExpression("vort_x","dw[1] - dv[2]")
    DefineScalarExpression("vort_y","du[2] - dw[0]")
    DefineScalarExpression("vort_z","dv[0] - du[1]")
    DefineScalarExpression("vort_mag","sqrt(vort_x*vort_x + vort_y*vort_y + vort_z*vort_z)")
    AddPlot("Pseudocolor","vort_mag")
    DrawPlots()

def main():
    #exe_3d("../../rt3d_small_chunk.silo")
    exe_3d("../../rt3d_one_chunk.silo")


if __visit_script_file__ == __visit_source_file__:
    main()

    
