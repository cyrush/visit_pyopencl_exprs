#!/usr/bin/env python

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