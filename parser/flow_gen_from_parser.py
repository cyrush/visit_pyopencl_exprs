#!/usr/bin/env python
#
# ${disclaimer}
#
"""
 file: flow_gen_from_parser.py
 author: Maysam Moussalem <maysam@tacc.utexas.edu>

 description:
  Takes a VisIt expression, parses it and builds a flow from it.

  Usage:
    python flow_gen_from_parser.py "mult(a, cos(b))"

"""

import sys
from visit_exprs_parser_prec import parse

# global variables
gen_code = ""
filter_id = 0

def print_to_file(code):
    """ Prints generated flow code to a new Python script.
    
    Arg:
       new_code: String containing generated code.
    """
    output = open('test.py', 'w')
    output.write(code)
    output.close()

def init_flow_code():
    """ Appends standard flow init code.
    """
    global gen_code
    gen_code += "import numpy as npy\n"
    gen_code += "from flow import *\n"
    gen_code += "from flow.filters import pyocl_ops, pyocl_compile\n\n"
    gen_code += "def setup_workspace():\n"
    gen_code += "    w = Workspace()\n"
    gen_code += "    w.register_filters(pyocl_compile)\n"
    gen_code += "    ctx  = w.add_context(\"pyocl_compile\",\"root\")\n"
    gen_code += "    ctx.start()\n"
    return gen_code

def create_numpy_data_array(arg_id):
    """ Create a NumPy array for input data.
    
    Arg:
       arg_id: Name of input data array.
    """
    global gen_code
    gen_code += "    v_" + str(arg_id) + " = npy.array(range(10),dtype=npy.float32)\n"

def add_data_source(arg_id):
    """ Create a data source in the flow network.
    
    Arg:
       arg_id: Name of input data array.
    """
    global gen_code
    gen_code += "    ctx.registry_add(\":" + str(arg_id) + "\",v_" + str(data_id) + ")\n"

def add_filter(op, filter_id):
    """ Create a filter corresponding to an operation in the flow network.

    Args:
       op: Name of operation to be added to flow network.
       filter_id: Id of filter to be added to flow network.
    """
    global gen_code
    gen_code += "    ctx.add_filter(\"" + str(op) + "\", \"f" + str(filter_id) + "\")\n"

def connect_filter(arg, arg_id, filter_id):
    """ Connect data source to a filter in flow network.

    Args:
       arg: Input data.
       arg_id: Input id.
       filter_id: Id of filter to be added to flow network.
    """
    global gen_code
    gen_code += "    ctx.connect(\":" + str(arg) + "\",(\"f" + str(filter_id) + "\",%d)" % arg_id + ")\n"

def complete_flow_code():
    """ Add remaining lines of code.
    """
    global gen_code
    gen_code += "    return w;\n"

def create_flow(parsed_expr):
    """ Generates flow network code for data sources and filters from parser output.

    Arg:
       parsed_expr: Parsed VisIt expression tree root.

    Returns:
       filter_id: Id of current filter which could be used as input to another filter.
    """
    global gen_code
    global filter_id
    filter_id += 1

    current_filter_id = filter_id
    add_filter(parsed_expr.name, filter_id)

    for i in range(len(parsed_expr.args)):
        if (str(parsed_expr.args[i].__class__.__name__) == "FuncCall"):
            connect_filter("f" + str(create_flow(parsed_expr.args[i])), i, current_filter_id)
        elif (str(parsed_expr.args[i].__class__.__name__) == "Id"):
            connect_filter(str(parsed_expr.args[i].name), i, current_filter_id)
        else:
            connect_filter(str(parsed_expr.args[i].value), i, current_filter_id)

    return current_filter_id

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Usage: python flow_gen_from_parser.py python flow_gen_from_parser.py \"mult(a, cos(b))\"")
    else:
        expr = sys.argv[1]
        
        # initialize flow network code
        gen_code = init_flow_code()
        
        # parse input expression
        parsed_expr = parse(expr)
        print "parsed_expr = ", parsed_expr
        
        # generate flow network from parsed expression
        create_flow(parsed_expr)

        # complete flow network code
        complete_flow_code()
        
        # print full code to a new Python script
        print_to_file(gen_code)
