#
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
        print "usage: run_generator.py [expr_file]"
        sys.exit(-1)
    args  = sys.argv[1:]
    nargs = len(args)
    expr  = open(args[0]).read()
    if "--build" in args:
        # build py packages
        sexe("visit -noconfig -nowin -cli -s setup.py build")
    sys.path.append("build/lib")
    import flow
    stmts = flow.Parser.parse(expr)
    print "Parser Statments:"
    for s in stmts:
        print s
    print "\n"
    print "Filter Network:"
    filters = flow.Generator.parse_network(expr)
    for f in filters:
        print f
    print "# of filters: %d" % len(filters)

if __name__ == "__main__":
    main()
