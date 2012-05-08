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

def save_window():
    ResetView()
    v = GetView3D()
    v.RotateAxis(0,-90)
    SetView3D(v)
    swatts= SaveWindowAttributes()
    swatts.outputToCurrentDirectory = 1
    swatts.outputDirectory = "."
    swatts.fileName = "chunk_render"
    swatts.family = 0
    swatts.format = swatts.PNG
    swatts.width = 1024
    swatts.height = 1024
    swatts.screenCapture = 0
    swatts.saveTiled = 0
    swatts.quality = 100
    swatts.progressive = 0
    swatts.binary = 0
    swatts.stereo = 0
    swatts.compression = swatts.PackBits
    swatts.forceMerge = 0
    swatts.resConstraint = swatts.NoConstraint
    swatts.advancedMultiWindowSave = 0
    SetSaveWindowAttributes(swatts)
    SaveWindow()


def exe_3d(db):
    OpenDatabase(db)
    DefineScalarExpression("vel_mag","sqrt(vx*vx + vy*vy+ vz*vz)")
    AddPlot("Pseudocolor","vel_mag")
    DrawPlots()
    if "-save" in Argv():
        save_window()
    if "-nowin" in sys.argv:
        sys.exit(0)

def main(db):
    #exe_3d("../../rt3d_small_chunk.silo")
    exe_3d(db)

if __visit_script_file__ == __visit_source_file__:
    args = Argv()
    db = "../../rt3d_one_chunk.silo"
    if len(args) > 0:
        db = args[0]
    main(db)



