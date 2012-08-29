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
    def __init__(self):
        self.reset()
    def reset(self):
        self.__count = 0
        self.__vmaps = {}
    def parse_network(self,txt):
        self.reset()
        stmts = parser.parse(txt)
        self.create_network(stmts)
    def create_network(self,stmts):
        res = []
        for expr in stmts:
            if isinstance(expr,parser.FuncCall):
                args = self.create_network(expr.args)
                fname = "f%d" % self.__count
                print fname,"=", expr.name,"(",args,")"
                res.append(fname)
                self.__count +=1
            if isinstance(expr,parser.Assignment):
                res = self.create_network([expr.value])
                print expr.name, ":=", res[0]
                self.__vmaps[expr.name] = res[0]
            if isinstance(expr,parser.Identifier):
                if expr.name in self.__vmaps.keys():
                    print expr.name, ":=", self.__vmaps[expr.name] 
                    iname =  self.__vmaps[expr.name] 
                else:
                    iname = ":" + expr.name
                res.append(iname)
            if isinstance(expr,list):
                rvals = self.create_network(expr)
                res.extend(rvals)
            if isinstance(expr,parser.Constant):
                res.append(expr.value)
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
    Generator().parse_network(txt)