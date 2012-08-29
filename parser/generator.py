#!/usr/bin/env python
#
# ${disclaimer}
#
"""
 File: generator.py
 Author: Cyrus Harrison, <cyrush@llnl.gov> 
         Maysam Moussalem <maysam@tacc.utexas.edu>

 Description:
  Takes a list of expressions, parses them and builds a data flow network specification.

  Usage:
   Command Line:
   > python generator.py "vx = a(2,3) + b^3 + 4 * var"
   (or)
   > python generator.py example_expr.txt
   From python:
   >>> import generator
   >>> print generator.Generator().parse_network("vx = a(2,3) + b^3 + 4 * var")


"""
import sys
import os
import parser

class Generator(object):
    @classmethod
    def parse_network(cls,txt):
        res = []
        stmts = parser.parse(txt)
        cls.create_network(stmts,res)
        return res
    @classmethod
    def create_network(cls,stmts,filters,count=None,vmaps=None):
        if count is None: count = [0]
        if vmaps is None: vmaps = {}
        res = []
        for expr in stmts:
            if isinstance(expr,parser.FuncCall):
                args = cls.create_network(expr.args,filters,count,vmaps)
                fname = "f%d" % count[0]
                print fname,"=", expr.name,"(",args,")"
                filters.append([fname, parser.FuncCall(expr.name, args)])
                res.append(parser.Identifier(fname))
                count[0]+=1
            if isinstance(expr,parser.Assignment):
                res = cls.create_network([expr.value],filters,count,vmaps)
                print expr.name, ":=", res[0]
                vmaps[expr.name] = res[0]
            if isinstance(expr,parser.Identifier):
                if expr.name in vmaps.keys():
                    print expr.name, ":=", vmaps[expr.name]
                    iname =  vmaps[expr.name] 
                else:
                    iname = ":" + expr.name
                res.append(parser.Identifier(iname))
            if isinstance(expr,list):
                rvals = cls.create_network(expr,filters,count,vmaps)
                res.extend(rvals)
            if isinstance(expr,parser.Constant):
                res.append(expr)
        return res

if __name__ == "__main__":
    txt = sys.argv[1]
    if os.path.isfile(txt):
        txt = open(txt).read()
    print "Parsing:\n" , txt, "\n"
    print "\nResult:"
    stmts = parser.parse(txt)
    for r in stmts:
        print " ",r
    print "\nNetwork:"
    filters = Generator.parse_network(txt)
    for f in filters:
        print f