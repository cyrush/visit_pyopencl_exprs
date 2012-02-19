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

def exe_2d(db):
    OpenDatabase(db)
    mesh_name = GetMetaData(db).GetMeshes(0).name
    DefineVectorExpression("mesh_coords","coord(%s)" % mesh_name)
    # we don't have a vel vector in this dataset
    # we will just exec curl on fake gradient field
    DefineVectorExpression("dfx","gradient(d)")
    DefineVectorExpression("dfy","gradient(p)")
    fvpe = "visit_pyopencl_curl_2d.vpe"
    DefinePythonExpression("c2d",
                           source="PythonFilter.load('%s')\n" % fvpe,
                           args=["dfx","dfy"])
    AddPlot("Pseudocolor","c2d")
    DrawPlots()

def exe_3d(db):
    OpenDatabase(db)
    mesh_name = GetMetaData(db).GetMeshes(0).name
    DefineVectorExpression("mesh_coords","coord(%s)" % mesh_name)
    # we don't have a vel vector in this dataset
    # we will just exec curl on fake gradient field
    DefineVectorExpression("dfx","gradient(d)")
    DefineVectorExpression("dfy","gradient(p)")
    DefineVectorExpression("dfz","gradient(p)")
    fvpe = "visit_pyopencl_curl_3d.vpe"
    DefinePythonExpression("c3d",
                            source="PythonFilter.load('%s')\n" % fvpe,
                            args=["dfx","dfy","dfz"],type="vector")
    DefineScalarExpression("c3d_x","c3d[0]")
    DefineScalarExpression("c3d_y","c3d[1]")
    DefineScalarExpression("c3d_z","c3d[2]")
    DefineScalarExpression("c3d_mag","magnitude(c3d)")
    AddPlot("Pseudocolor","c3d_mag")
    DrawPlots()


def main():
    exe_2d("../../tests/data/rect2d.silo")
    AddWindow()
    exe_3d("../../tests/data/rect3d.silo")
        
if __visit_script_file__ == __visit_source_file__:
    main()

    
