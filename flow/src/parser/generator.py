#!/usr/bin/env python
#
# ${disclaimer}
#
"""
 File: generator.py
 Authors: Cyrus Harrison, <cyrush@llnl.gov>
         Maysam Moussalem <maysam@tacc.utexas.edu>

 Description:
  Takes a list of expressions, parses them and builds a data flow
  network specification.

 Usage:
   >>> from generator import *
   >>> print Generator.parse_network("vx = a(2,3) + b^3 + 4 * var")

"""
import sys
import os
from parser import *

class Generator(object):
    @classmethod
    def parse_network(cls,txt,ctx=None):
        res = []
        stmts = Parser.parse(txt)
        cls.__create_network(stmts,res)
        if not ctx is None:
            cls.__setup_context(res,ctx)
        return res
    @classmethod
    def __create_network(cls,stmts,filters,count=None,vmaps=None):
        if count is None: count = [0]
        if vmaps is None: vmaps = {}
        res = []
        for expr in stmts:
            if isinstance(expr,FuncCall):
                args = cls.__create_network(expr.args,filters,count,vmaps)
                fname = "f%d" % count[0]
                print fname,"=", expr.name,"(",args,",",expr.params,")"
                filters.append([fname, FuncCall(expr.name, args, expr.params)])
                res.append(Identifier(fname))
                count[0]+=1
            if isinstance(expr,Assignment):
                res = cls.__create_network([expr.value],filters,count,vmaps)
                print expr.name, ":=", res[0]
                vmaps[expr.name] = res[0].name
            if isinstance(expr,Identifier):
                if expr.name in vmaps.keys():
                    iname =  vmaps[expr.name]
                else:
                    iname = ":" + expr.name
                res.append(Identifier(iname))
            if isinstance(expr,list):
                rvals = cls.__create_network(expr,filters,count,vmaps)
                res.extend(rvals)
            if isinstance(expr,Constant):
                fname = "c%d" % count[0]
                print fname,"=", "const([]",",", {"value":expr.value},")"
                filters.append([fname, FuncCall("const", [], {"value":expr.value})])
                res.append(Identifier(fname))
                count[0]+=1
        return res
    @classmethod
    def __setup_context(cls,filters,ctx):
        for f in filters:
            fname = f[0]
            fcall = f[1]
            ctx.add_filter(fcall.name,fname,fcall.params)
            idx = 0
            for arg in fcall.args:
                if isinstance(arg,Identifier):
                    ctx.connect(arg.name,(fname,idx))
                    idx+=1
