#!/usr/bin/env python

import sys
import os
import subprocess
from   os.path import join as pjoin

def sexe(cmd):
    print "[exec: %s]" % cmd
    subprocess.call(cmd,shell=True)

def main():
    if len(sys.argv) < 2:
        print "usage: run_flow_vpe_workspace.py [expr] <plat:dev> <dbfile> <fset>"
        sys.exit(-1)
    args    = sys.argv[1:]
    nargs   = len(args)
    wscript = os.path.abspath(args[0])
    dbfile  = ""
    fset    = ""
    plat    = 0
    dev     = 1
    if nargs > 1:
        dbfile = os.path.abspath(args[1])
    if nargs > 2:
        fset = args[2]
    # build py packages
    os.chdir("flow")
    sexe("visit -noconfig -nowin -cli -s setup.py build")
    os.chdir(pjoin("..","visit_flow_vpe"))
    sexe("visit -noconfig -nowin -cli -s setup.py build")
    os.chdir("..")
    # set env vars
    pypath = pjoin(os.getcwd(),"flow","build","lib")
    pypath += ":" + pjoin(os.getcwd(),"visit_flow_vpe","build","lib")
    if os.environ.has_key("PYTHONPATH"):
        pypath = os.environ["PYTHONPATH"] + ":" + pypath
    os.environ["PYTHONPATH"] = pypath
    rscript = os.path.abspath(pjoin(os.getcwd(),
                                    "visit_flow_vpe",
                                    "visit_exec_example_workspace.py"))
    sexe("visit -cli -s %s %s %s %s %d:%d" % (rscript,wscript,dbfile,fset,plat,dev))


if __name__ == "__main__":
    main()