#*****************************************************************************
#
# Copyright (c) 2000 - 2012, Lawrence Livermore National Security, LLC
# Produced at the Lawrence Livermore National Laboratory
# LLNL-CODE-442911
# All rights reserved.
#
# This file is  part of VisIt. For  details, see https://visit.llnl.gov/.  The
# full copyright notice is contained in the file COPYRIGHT located at the root
# of the VisIt distribution or at http://www.llnl.gov/visit/copyright.html.
#
# Redistribution  and  use  in  source  and  binary  forms,  with  or  without
# modification, are permitted provided that the following conditions are met:
#
#  - Redistributions of  source code must  retain the above  copyright notice,
#    this list of conditions and the disclaimer below.
#  - Redistributions in binary form must reproduce the above copyright notice,
#    this  list of  conditions  and  the  disclaimer (as noted below)  in  the
#    documentation and/or other materials provided with the distribution.
#  - Neither the name of  the LLNS/LLNL nor the names of  its contributors may
#    be used to endorse or promote products derived from this software without
#    specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT  HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR  IMPLIED WARRANTIES, INCLUDING,  BUT NOT  LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND  FITNESS FOR A PARTICULAR  PURPOSE
# ARE  DISCLAIMED. IN  NO EVENT  SHALL LAWRENCE  LIVERMORE NATIONAL  SECURITY,
# LLC, THE  U.S.  DEPARTMENT OF  ENERGY  OR  CONTRIBUTORS BE  LIABLE  FOR  ANY
# DIRECT,  INDIRECT,   INCIDENTAL,   SPECIAL,   EXEMPLARY,  OR   CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT  LIMITED TO, PROCUREMENT OF  SUBSTITUTE GOODS OR
# SERVICES; LOSS OF  USE, DATA, OR PROFITS; OR  BUSINESS INTERRUPTION) HOWEVER
# CAUSED  AND  ON  ANY  THEORY  OF  LIABILITY,  WHETHER  IN  CONTRACT,  STRICT
# LIABILITY, OR TORT  (INCLUDING NEGLIGENCE OR OTHERWISE)  ARISING IN ANY  WAY
# OUT OF THE  USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH
# DAMAGE.
#*****************************************************************************
"""
 file: visit_pyopencl_grad_exec.py
 author: Cyrus Harrison <cyrush@llnl.gov>
 created: 2/17/2012

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
    DefineVectorExpression("du","gradient(vx)")
    DefineVectorExpression("dv","gradient(vy)")
    DefineVectorExpression("dw","gradient(vz)")
    # s tensor
    DefineScalarExpression("s_0","du[0]")
    DefineScalarExpression("s_1",".5 * (du[1] + dv[0])")
    DefineScalarExpression("s_2",".5 * (du[2] + dw[0])")
    #
    DefineScalarExpression("s_3",".5 * (dv[0] + du[1])")
    DefineScalarExpression("s_4","dv[1]")
    DefineScalarExpression("s_5",".5 * (dv[2] + dw[1])")
    #
    DefineScalarExpression("s_6",".5 * (dw[0] + du[2])")
    DefineScalarExpression("s_7",".5 * (dw[1] + dv[2])")
    DefineScalarExpression("s_8","dw[2]")
    # w tensor
    DefineScalarExpression("w_1",".5 * (du[1] - dv[0])")
    DefineScalarExpression("w_2",".5 * (du[2] - dw[0])")
    #
    DefineScalarExpression("w_3",".5 * (dv[0] - du[1])")
    DefineScalarExpression("w_5",".5 * (dv[2] - dw[1])")
    #
    DefineScalarExpression("w_6",".5 * (dw[0] - du[2])")
    DefineScalarExpression("w_7",".5 * (dw[1] - dv[2])")
    # Frobenius norms
    DefineScalarExpression("s_norm","s_0*s_0 + s_1*s_1 + s_2*s_2+ s_3*s_3 + s_4*s_4 + s_5*s_5 + s_6*s_6 + s_7*s_7 + s_8*s_8")
    DefineScalarExpression("w_norm","w_1*w_1 + w_2*w_2+ w_3*w_3 + w_5*w_5 + w_6*w_6 + w_7*w_7")
    #
    DefineScalarExpression("q_crit",".5 * (w_norm - s_norm)")
    AddPlot("Pseudocolor","q_crit")
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
    db = "../../rt3d_small_chunk.silo"
    if len(args) > 0:
        db = args[0]
    main(db)



