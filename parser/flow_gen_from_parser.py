#!/usr/bin/env python
#
# ${disclaimer}
#
"""
 File: flow_gen_from_parser.py
 Author: Maysam Moussalem <maysam@tacc.utexas.edu>

 Description:
  Takes a list of VisIt expressions, parses them and builds a flow from them.

 Usage:
  python flow_gen_from_parser.py expressions.txt generated_flow.py.

"""

import sys
from visit_exprs_parser_prec import parse

# global variables
gen_code = ""
filter_id = 0
filter_list = []

def print_to_file(code, output_file):
    """ Prints generated flow code to a new Python script.
    
    Arg:
       code: String containing generated code.
       output_file: Python file to which generated code is to be written.
    """
    output = open(output_file, 'w')
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

def complete_flow_code():
    """ Add remaining line(s) of code.
    """
    global gen_code
    gen_code += "    return w;\n"

def get_flow_code(expr):
    """ Return the string containing the flow code.
    Can be used for testing.

    Arg:
       expr: Expression which will be parsed and from which a flow will be generated.
    """
    global gen_code
    global filter_id
    global filter_list
    # reset global vars here (important for unit testing)
    gen_code = ""
    filter_id = 0
    filter_list = []
    parsed_expr, vmaps = parse(expr)
    create_flow(parsed_expr, vmaps)
    return gen_code

def create_numpy_data_array(arg_id):
    """ Create a NumPy array for input data.
    
    Arg:
       arg_id: Name of input data array.
    """
    global gen_code
    gen_line = "    v_" + str(arg_id) + " = npy.array(range(10),dtype=npy.float32)\n"
    gen_code += gen_line
    return gen_line

def add_data_source(arg_id):
    """ Create a data source in the flow network.
    
    Arg:
       arg_id: Name of input data array.
    """
    global gen_code
    gen_line = "    ctx.registry_add(\":" + str(arg_id) + "\",v_" + str(arg_id) + ")\n"
    gen_code += gen_line
    return gen_line

def add_filter(op, filter_id):
    """ Create a filter corresponding to an operation in the flow network.

    Args:
       op: Name of operation to be added to flow network.
       filter_id: Id of filter to be added to flow network.
    """
    global gen_code
    gen_line = "    ctx.add_filter(\"" + str(op) + "\", \"" + str(filter_id) + "\")\n"
    gen_code += gen_line
    return gen_line

def add_decompose_filter(op, filter_id, index):
    """ Create a filter corresponding to a decomposition in the flow network.

    Args:
       op: Name of operation to be added to flow network: "decompose" in this case.
       filter_id: Id of filter to be added to flow network.
       index: Index used in decomposition.
    """
    global gen_code
    gen_line = "    ctx.add_filter(\"" + str(op) + "\", \"" + str(filter_id) + "\", {\"index\":" + str(index) + "})\n"
    gen_code += gen_line
    return gen_line

def connect_filter_var(arg, arg_id, filter_id):
    """ Connect data source to a filter in the flow network. Data source is a variable
    available in the database (Id).

    Args:
       arg: Input data.
       arg_id: Input id.
       filter_id: Id of filter to be added to flow network.
    """
    global gen_code
    gen_line = "    ctx.connect(\":" + str(arg) + "\",(\"" + str(filter_id) + "\",%d)" % arg_id + ")\n"
    gen_code += gen_line
    return gen_line

def connect_filter(arg, arg_id, filter_id):
    """ Connect data source to a filter in the flow network. Data source is the result of
    another filter or a constant value.

    Args:
       arg: Input data.
       arg_id: Input id.
       filter_id: Id of filter to be added to flow network.
    """
    global gen_code
    gen_line = "    ctx.connect(\"" + str(arg) + "\",(\"" + str(filter_id) + "\",%d)" % arg_id + ")\n"
    gen_code += gen_line
    return gen_line

def create_flow(parsed_expr, var_mapping):
    """ Generates flow network code for data sources and filters from parser output.

    Arg:
       parsed_expr: Parsed VisIt expression tree root.
       var_mapping: Variable mappings to use in the case of assignment.

    Returns:
       filter_id: Id of current filter which could be used as input to another filter.
    """
    global gen_code
    global filter_id
    global filter_list
    is_assignment = False
    assigned_filter = ''

    # check if this is an assignment operation
    for key, item in var_mapping.iteritems():
        if (str(parsed_expr) == str(item)):
            is_assignment = True
            assigned_filter = str(key)

    # start out by processing op at root of parse tree
    if (is_assignment):
        current_filter_id = assigned_filter
        add_filter(parsed_expr.name, current_filter_id)
        is_assignment = False
    elif (parsed_expr.name == "decompose"):
        filter_id += 1
        current_filter_id = "f" + str(filter_id)
        add_decompose_filter(parsed_expr.name, current_filter_id, parsed_expr.args[1].value)
    else:
        filter_id += 1
        current_filter_id = "f" + str(filter_id)
        add_filter(parsed_expr.name, current_filter_id)
    filter_list.append(current_filter_id)

    # then process operation's parameters
    if (parsed_expr.name == "decompose"):
        if (str(parsed_expr.args[0].__class__.__name__) == "FuncCall"):
            connect_filter(str(create_flow(parsed_expr.args[0], var_mapping)), 0, current_filter_id)
        elif (str(parsed_expr.args[0].__class__.__name__) == "Id"):
            if (str(parsed_expr.args[0].name) in filter_list):
                connect_filter(str(parsed_expr.args[0].name), 0, current_filter_id)
            else:
                connect_filter_var(str(parsed_expr.args[0].name), 0, current_filter_id)
        else:
            connect_filter(str(parsed_expr.args[0].value), 0, current_filter_id)
    else:
        for i in range(len(parsed_expr.args)):
            if (str(parsed_expr.args[i].__class__.__name__) == "FuncCall"):
                connect_filter(str(create_flow(parsed_expr.args[i], var_mapping)), i, current_filter_id)
            elif (str(parsed_expr.args[i].__class__.__name__) == "Id"):
                if (str(parsed_expr.args[i].name) in filter_list):
                    connect_filter(str(parsed_expr.args[i].name), i, current_filter_id)
                else:
                    connect_filter_var(str(parsed_expr.args[i].name), i, current_filter_id)
            else:
                connect_filter(str(parsed_expr.args[i].value), i, current_filter_id)

    return current_filter_id

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Usage: python flow_gen_from_parser.py expressions.txt generated_flow.py.")
    else:
        expr_file = sys.argv[1]
        output_file = sys.argv[2]
        
        # read through file, store expressions in list
        input = open(str(expr_file), 'r')
        list = input.readlines()

        # initialize flow network code
        gen_code = init_flow_code()
        
        # process expressions one by one
        for expr in list:
            
            # parse input expression
            parsed_expr, vmaps = parse(expr)
            print "parsed_expr = ", parsed_expr
            print "vmaps = ", vmaps
            
            # generate flow network from parsed expression
            create_flow(parsed_expr, vmaps)

        # complete flow network code
        complete_flow_code()
        
        # print full code to a new Python script
        print_to_file(gen_code, output_file)
