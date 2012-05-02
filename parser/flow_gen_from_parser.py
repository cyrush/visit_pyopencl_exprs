#!/usr/bin/env python
#
# ${disclaimer}
#
"""
 file: flow_gen_from_parser.py
 authors: Maysam Moussalem <maysam@tacc.utexas.edu>

 description:
  Takes a VisIt expression, parses it and builds a flow from it.

  Usage:
    python flow_gen_from_parser.py "a(2,3) + b^3 + 4 * var"

"""

import sys
from visit_exprs_parser_prec import parse

# global variables
gen_code = ""
op_id = 0
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

def create_numpy_data_array(data_id):
    """ Create a NumPy array for input data.
    
    Args:
       data_id: Name of input data array.
       code: Generated code to append to.
    """
    global gen_code
    gen_code += "    v_" + str(data_id) + " = npy.array(range(10),dtype=npy.float32)\n"

def add_data_source(data_id):
    """ Create a data source in the flow network.
    
    Arg:
       data_id: Name of input data array.
    """
    global gen_code
    gen_code += "    ctx.registry_add(\":src_" + str(data_id) + "\",v_" + str(data_id) + ")\n"

def add_filter(op, op_id):
    """ Create a filter corresponding to an operation to the flow network.

    Args:
       op: Name of operation to be added to flow network.
       op_id: Id of operation to be added to flow network.
    """
    global gen_code
    gen_code += "    ctx.add_filter(\"" + str(op) + "\", \"f" + str(op_id) + "\")\n"

def connect_filter(op, op_id, data_list):
    """ Connect data sources and filter in flow network.

    Args:
       op: Name of operation to be added to flow network.
       op_id: Id of operation to be added to flow network.
       data_list: List of input data
    """
    global gen_code
    for i in range(len(data_list)):
        # TODO: adjust data source naming here -- could be of form src_x or f1...
        gen_code += "    ctx.connect(\":" + str(data_list[i]) + "\",(\"f" + str(op_id) + "\",%d)" % i + ")\n"

def complete_flow_code():
    """ Add remaining lines of code.
    """
    global gen_code
    gen_code += "    return w;\n"

def create_flow_network(parser_output, filter_id):
    """ Generates flow network code for data sources and filters from parser output.

    Arg:
       parser_output: Parsed VisIt expression.
       filter_id: id given to this filter
    """
    #global filter_id
    global gen_code
    
    # recursively process parser output:
    # op([sub_expr, sub_expr, ...]) where a sub_expr can be an arg

    # base case: 1 op with 1 set of args
    # (i.e. only 1 set of matching "([])" brackets)
    num_sub_exprs = parser_output.count("([")
    
    if (num_sub_exprs == 1):
        # can create data sources, filter and connect them
        filter_name = "f" + str(filter_id)
        
        # pull out the op
        op = parser_output[0:parser_output.find("([")]
        # get list of arguments
        args = parser_output[parser_output.find("([")+2:parser_output.find("])")]
        args_list = args.split(",")
        
        # now append commands to generated code
        
        # data source(s)
        #for i in range(len(args_list)):
        #    create_numpy_data_array(str(args_list[i]))
        #    add_data_source(str(args_list[i]))
        # filter
        add_filter(str(op), filter_id)
        # connect filter and data source(s)
        connect_filter(op, filter_id, args_list)
        
    # recursion: pick out op, then call function recursively on each sub-expr
    else:
        op = parser_output[0:parser_output.find("([")]
        # count number of args: can do by removing outermost brackets, then
        # counting commas not surrounded by double-brackets
        # keep bracket counter, with +1 for left, -1 for right
        num_sub_exprs = 0
        sub_exprs = []
        counter = 0
        start = 0
        exprs = parser_output[parser_output.find("([")+2:parser_output.find("])")]

        for i in range(len(exprs)):
            if (exprs[i] == "["):
                counter += 1
            elif (exprs[i] == "]"):
                counter -= 1
            elif (exprs[i] == ","):
                if (counter == 0):
                    # we've found an arg
                    sub_exprs[num_sub_exprs] = exprs[start:i]
                    num_sub_exprs += 1
                    # update start to be right after comma
                    start = i + 1
            # otherwise do nothing

        # recursive call
        for i in range(num_sub_exprs):
            filter_id += 1
            create_flow_network(sub_exprs[i], filter_id)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Usage: python flow_gen_from_parser.py expr")
    else:
        expr = sys.argv[1]
        
        # initialize flow network code
        gen_code = init_flow_code()
        
        # parse input expression
        # gives an error -- is this because of format of parser output?
        parsed_expr = parse(expr)
        print parsed_expr
        # can test with these instead
        #parsed_expr = "+([a, b])"
        #parsed_expr = "+([a([const(2), const(3)]), ^([b, +([const(3), *([const(4), var])])])])"
        #parsed_expr = "grad([vx,dims,x,y,z])"
        
        # generate flow network from parsed expression
        create_flow_network(parsed_expr , filter_id)

        # complete flow network code
        complete_flow_code()
        
        # print full code to a new Python script
        print_to_file(gen_code)
