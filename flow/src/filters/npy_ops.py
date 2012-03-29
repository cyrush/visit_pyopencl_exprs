#
# ${disclaimer}
#
"""
 file: npy_ops.py
 author: Cyrus Harrison <cyrush@llnl.gov>
 created: 12/09/2011
 description:
    Provides flow filters that execute numpy operations.

"""

# Guarded import of numpy
found_numpy = False
try:
    import numpy as npy
    found_numpy = True
except ImportError:
    pass

from ..core import Filter


class NPyAdd(Filter):
    filter_type    = "add"
    input_ports    = ["in_a","in_b"]
    default_params = {}
    output_port    = True
    def execute(self):
        return self.input("in_a") + self.input("in_b")

class NPySub(Filter):
    filter_type    = "sub"
    input_ports    = ["in_a","in_b"]
    default_params = {}
    output_port    = True
    def execute(self):
        return self.input("in_a") - self.input("in_b")

class NPyMult(Filter):
    filter_type    = "mult"
    input_ports    = ["in_a","in_b"]
    default_params = {}
    output_port    = True
    def execute(self):
        return self.input("in_a") * self.input("in_b")

class NPyPow(Filter):
    filter_type    = "pow"
    input_ports    = ["in_a","in_b"]
    default_params = {}
    output_port    = True
    def execute(self):
        return npy.power(self.input("in_a"),self.input("in_b"))

class NPySin(Filter):
    filter_type    = "sin"
    input_ports    = ["in"]
    default_params = {}
    output_port    = True
    def execute(self):
        return npy.sin(self.input("in"))

class NPyCos(Filter):
    filter_type    = "cos"
    input_ports    = ["in"]
    default_params = {}
    output_port    = True
    def execute(self):
        return npy.cos(self.input("in"))


filters = [NPyAdd,
           NPySub,
           NPyMult,
           NPyPow,
           NPySin,
           NPyCos]
