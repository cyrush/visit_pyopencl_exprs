#
# ${disclaimer}
#
"""
 file: npy_ops.py
 author: Cyrus Harrison <cyrush@llnl.gov>
 created: 3/24/2012
 description:
    Provides flow filters that compile and execute numpy operations.

"""

# Guarded import of numpy
found_numpy = False
try:
    import numpy as npy
    found_numpy = True
except ImportError:
    pass

from ..core import Filter, Context, log

def info(msg):
    log.info(msg,"filters.npy_compile")

class NPyCompileContext(Context):
    context_type = "npy_compile"
    def start(self):
        self.vars  = []
        self.stmts = []
    def bind_data(self,obj):
        # gen name
        idx = len(self.vars)
        var_name  = "_auto_var_%04d" % idx
        self.vars.append((var_name, obj))
        self.stmts.append("%s = bindings[%s][1]" % (var_name,idx))
        return var_name
    def add_statement(self,stmt):
        res_name  = "_auto_res_%04d" % len(self.stmts)
        self.stmts.append(res_name + " = " + stmt)
        return res_name
    def compile(self):
        res = ""
        for stmt in self.stmts:
            res += "%s\n" % stmt
        return res
    def run(self):
        src = self.compile()
        msg  = "Execute Python:\n"
        msg += src
        info(msg)
        bindings = self.vars
        exec(src,locals())
        return locals()["_auto_res_%04d" % (len(self.stmts)-1)]

class NPySource(Filter):
    # overrides standard RegistrySource
    filter_type    = "<registry_source>"
    input_ports    = []
    default_params = {}
    output_port    = True
    def execute(self):
        # fetch data from registry 
        # the instance name determines the reg entry_key
        key  = self.name[self.name.rfind(":"):]
        data = self.context.registry_fetch(key)
        # bind var into the context
        var_name = self.context.bind_data(data)
        return var_name

class NPyAdd(Filter):
    filter_type    = "add"
    input_ports    = ["in_a","in_b"]
    default_params = {}
    output_port    = True
    def execute(self):
        return self.context.add_statement("(%s + %s) " % (self.input("in_a"),self.input("in_b")))
        

class NPySub(Filter):
    filter_type    = "sub"
    input_ports    = ["in_a","in_b"]
    default_params = {}
    output_port    = True
    def execute(self):
        return self.context.add_statement("(%s - %s) " % (self.input("in_a"),self.input("in_b")))

class NPyMult(Filter):
    filter_type    = "mult"
    input_ports    = ["in_a","in_b"]
    default_params = {}
    output_port    = True
    def execute(self):
        return self.context.add_statement("(%s * %s) " % (self.input("in_a"),self.input("in_b")))

class NPyPow(Filter):
    filter_type    = "pow"
    input_ports    = ["in_a","in_b"]
    default_params = {}
    output_port    = True
    def execute(self):
        return self.context.add_statement("npy.power(%s, %s) " % (self.input("in_a"),self.input("in_b")))

class NPySin(Filter):
    filter_type    = "sin"
    input_ports    = ["in"]
    default_params = {}
    output_port    = True
    def execute(self):
        return self.context.add_statement("npy.sin(%s)" % self.input("in"))

class NPyCos(Filter):
    filter_type    = "cos"
    input_ports    = ["in"]
    default_params = {}
    output_port    = True
    def execute(self):
        return self.context.add_statement("npy.cos(%s)" % self.input("in"))


filters = [NPySource,
           NPyAdd,
           NPySub,
           NPyMult,
           NPyPow,
           NPySin,
           NPyCos]

contexts = [NPyCompileContext]