#!/usr/bin/env python
#
# ${disclaimer}
#
"""
 file: npy_ops.py
 author: Cyrus Harrison <cyrush@llnl.gov>
 created: 12/09/2011
 description:
    TODO

"""

import numpy as npy
from ..core import Filter

class NPySource(Filter):
    name = "src"
    inputs = []
    default_params = {"data":None}
    output = True
    @classmethod
    def execute(cls,name,inputs,params):
        return params.data

class NPyAdd(Filter):
    name = "add"
    inputs = ["a","b"]
    default_params = {}
    output = True
    @classmethod
    def execute(cls,name,inputs,params):
        return inputs["a"] + inputs["b"]

class NPySub(Filter):
    name = "sub"
    inputs = ["a","b"]
    default_params = {}
    output = True
    @classmethod
    def execute(cls,name,inputs,params):
        return inputs["a"] - inputs["b"]

class NPyMult(Filter):
    name = "mult"
    inputs = ["a","b"]
    default_params = {}
    output = True
    @classmethod
    def execute(cls,name,inputs,params):
        return inputs["a"] * inputs["b"]

class NPyPow(Filter):
    name = "pow"
    inputs = ["a","b"]
    default_params = {}
    output = True
    @classmethod
    def execute(cls,name,inputs,params):
        return npy.power(inputs["a"],inputs["b"])

class NPySin(Filter):
    name = "sin"
    inputs = ["a"]
    default_params = {}
    output = True
    @classmethod
    def execute(cls,name,inputs,params):
        return npy.sin(inputs["a"])

class NPyCos(Filter):
    name = "cos"
    inputs = ["a"]
    default_params = {}
    output = True
    @classmethod
    def execute(cls,name,inputs,params):
        return npy.cos(inputs["a"])


filters = [NPySource,
           NPyAdd,
           NPySub,
           NPyMult,
           NPyPow,
           NPySin,
           NPyCos]
