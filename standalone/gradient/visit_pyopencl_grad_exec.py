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


