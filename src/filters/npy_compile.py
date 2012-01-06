#!/usr/bin/env python
#
# ${disclaimer}
#
"""
 file: npy_compile.py
 author: Cyrus Harrison <cyrush@llnl.gov>
 created: 12/09/2011
 description:
    TODO

"""

import numpy as npy
from ..core import Filter

__bind = {}

def reset_exe_env():
    global __bind
    __bind = {}
    return True

def bindings():
    global __bind
    return __bind

class NPyCompileSource(Filter):
    name = "src"
    inputs = []
    default_params = {"name":None}
    output = True
    @classmethod
    def execute(cls,name,inputs,params):
        global __bind
        bindings()[params.name] = params.data
        return params.name

class NPyCompileAdd(Filter):
    name = "add"
    inputs = ["a","b"]
    default_params = {}
    output = True
    @classmethod
    def execute(cls,name,inputs,params):
        return "(%s + %s)" % (inputs["a"],inputs["b"])

class NPyCompileSub(Filter):
    name = "sub"
    inputs = ["a","b"]
    default_params = {}
    output = True
    @classmethod
    def execute(cls,name,inputs,params):
        return "(%s - %s)" % (inputs["a"],inputs["b"])

class NPyCompileMult(Filter):
    name = "mult"
    inputs = ["a","b"]
    default_params = {}
    output = True
    @classmethod
    def execute(cls,name,inputs,params):
        return "(%s * %s)" % (inputs["a"],inputs["b"])

class NPyCompilePow(Filter):
    name = "pow"
    inputs = ["a","b"]
    default_params = {}
    output = True
    @classmethod
    def execute(cls,name,inputs,params):
        return "npy.power(%s,%s)" % (inputs["a"],inputs["b"])

class NPyCompileSin(Filter):
    name = "sin"
    inputs = ["a"]
    default_params = {}
    output = True
    @classmethod
    def execute(cls,name,inputs,params):
        return "npy.sin(%s)" % inputs["a"]

class NPyCompileCos(Filter):
    name = "cos"
    inputs = ["a"]
    default_params = {}
    output = True
    @classmethod
    def execute(cls,name,inputs,params):
        return "npy.cos(%s)" % inputs["a"]

class NPyCompileSink(Filter):
    name = "sink"
    inputs = ["expr"]
    default_params = {}
    output = True
    @classmethod
    def execute(cls,name,inputs,params):
        expr = "__res = " + inputs["expr"]
        print "[npy_compile: Result Expression: %s]" % expr
        exec("import numpy as npy",bindings())
        exec(expr,bindings())
        res = bindings()["__res"]
        reset_exe_env()
        return res

filters =  [NPyCompileSource,
            NPyCompileAdd,
            NPyCompileSub,
            NPyCompileMult,
            NPyCompilePow,
            NPyCompileSin,
            NPyCompileCos,
            NPyCompileSink]
