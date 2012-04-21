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
    DefineScalarExpression("x","mesh_coords[0]")
    DefineScalarExpression("y","mesh_coords[1]")
    fvpe = "visit_pyopencl_grad.vpe"
    DefinePythonExpression("g2d",
                           source="PythonFilter.load('%s')\n" % fvpe,
                           args=["x","y","d"],type="vector")
    DefineScalarExpression("g2d_x","g2d[0]")
    DefineScalarExpression("g2d_y","g2d[1]")
    AddPlot("Pseudocolor","g2d_x")
    DrawPlots()

def exe_3d(db):
    OpenDatabase(db)
    mesh_name = GetMetaData(db).GetMeshes(0).name
    DefineVectorExpression("mesh_coords","coord(%s)" % mesh_name)
    DefineScalarExpression("x","mesh_coords[0]")
    DefineScalarExpression("y","mesh_coords[1]")
    DefineScalarExpression("z","mesh_coords[2]")
    fvpe = "visit_pyopencl_grad.vpe"
    DefinePythonExpression("g3d",
                            source="PythonFilter.load('%s')\n" % fvpe,
                            args=["x","y","z","d"],type="vector")
    DefineScalarExpression("g3d_x","g3d[0]")
    DefineScalarExpression("g3d_y","g3d[1]")
    DefineScalarExpression("g3d_z","g3d[2]")
    AddPlot("Pseudocolor","g3d_x")
    DrawPlots()


def main():
    exe_2d("../../visit_flow_vpe/tests/_data/rect2d.silo")
    AddWindow()
    exe_3d("../../visit_flow_vpe/tests/_data/rect3d.silo")

        
if __visit_script_file__ == __visit_source_file__:
    main()

    
