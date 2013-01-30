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

import sys
import os
import subprocess
from   os.path import join as pjoin


def script_dir():
    return os.path.split(os.path.abspath(__file__))[0]

def sexe(cmd):
    print "[exec: %s]" % cmd
    subprocess.call(cmd,shell=True)

def main():
    if len(sys.argv) < 2:
        print "usage: run_flow_vpe_workspace.py [exprfile] <dbfile> <fset> <plat> <dev>"
        sys.exit(-1)
    args     = sys.argv[1:]
    nargs    = len(args)
    exprfile = os.path.abspath(args[0])
    dbfile   = ""
    fset     = ""
    plat     = 0
    dev      = 0
    sopt     = ""
    nopt     = ""
    vcmd     = "visit"
    if nargs > 1:
        dbfile = os.path.abspath(args[1])
    if nargs > 2:
        fset = args[2]
    if nargs > 3:
        plat = int(args[3])
    if nargs > 4:
        dev  = int(args[4])
    if "-save" in args:
        nopt = "-nowin"
        sopt = "-save"
    if "-par" in args:
        pargs = args[args.index("-par") + 1]
        vcmd += " %s " % pargs
    # build py packages
    cwd = os.getcwd()
    sdir = script_dir()
    os.chdir(pjoin(sdir,"flow"))
    sexe("visit -noconfig -nowin -cli -s setup.py build")
    os.chdir(pjoin(sdir,"visit_flow_vpe"))
    sexe("visit -noconfig -nowin -cli -s setup.py build")
    os.chdir(cwd)
    # set env vars
    pypath = pjoin(script_dir(),"flow","build","lib")
    pypath += ":" + pjoin(script_dir(),"visit_flow_vpe","build","lib")
    if os.environ.has_key("PYTHONPATH"):
        pypath = os.environ["PYTHONPATH"] + ":" + pypath
    os.environ["PYTHONPATH"] = pypath
    rscript = os.path.abspath(pjoin(script_dir(),
                                    "visit_flow_vpe",
                                    "visit_exec_example_workspace.py"))
    sexe("%s %s -cli -s %s %s %s %s %d %d %s" % (vcmd,nopt,rscript,exprfile,dbfile,fset,plat,dev,sopt))


if __name__ == "__main__":
    main()