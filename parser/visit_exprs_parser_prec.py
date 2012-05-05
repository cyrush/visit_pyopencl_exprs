#!/usr/bin/env python
#
# ${disclaimer}
#
"""
 file: visit_exprs_parser_prec.py
 authors: Cyrus Harrison <cyrush@llnl.gov>
          Maysam Moussalem <maysam@tacc.utexas.edu>

 description:
  ply (python lex & yacc) parser for VisIt's expression language.
  I used Mayam's visit_exprs.py as a starting point & adapted a subset
  of rules from VisIt's existing expression language parser:
   http://portal.nersc.gov/svn/visit/trunk/src/common/expr/ExprGrammar.C

 I also used this following tutorial as a reference:
  http://drdobbs.com/web-development/184405580

  Note: This version of the parser has additional rules deadling with
  precedence and (sub-)expression grouping.

  Usage:
   Command Line:
   > python visit_exprs_parser.py " a(2,3) + b^3 + 4 * var"
   From python:
   >>> from visit_exprs_parser import parse
   >>> print parse(" a(2,3) + b^3 + 4 * var")

"""

import sys
# note: we can install ply via setup.py install --prefix in the future
sys.path.insert(0,"ply-3.4")

import ply.lex as lex
import ply.yacc as yacc

vmaps = {}

class FuncCall(object):
    def __init__(self,name,args=None):
        self.name = name
        self.args = args
    def __str__(self):
        if self.args is None:
            return "<FuncCallObj>%s()" % (self.name)
        else:
            return "<FuncCallObj>%s(%s)" % (self.name, str(self.args))
    def __repr__(self):
       return str(self)

class Constant(object):
    def __init__(self,value):
        self.value = value
    def __str__(self):
        return "const(%s)" % str(self.value)
    def __repr__(self):
        return str(self)


class Id(object):
    def __init__(self,name):
        self.name = name
    def __str__(self):
        return str(self.name)
    def __repr__(self):
        return str(self)

tokens = ['INT',
          'FLOAT',
          'BOOL',
          'STRING',
          'ID',
          'PLUS',
          'MINUS',
          'MULT',
          'EXP',
          'GTE',
          'LTE',
          'GT',
          'LT',
          'EQ',
          'COMMA',
          'LPAREN',
          'RPAREN',
          'LBRACKET',
          'RBRACKET',
          'LBRACE',
          'RBRACE',
          'DECOMP'
          ]

t_PLUS   = r'\+'
t_MINUS  = r'-'
t_MULT   = r'\*'
t_EXP    = r'\^'

t_GTE    = r'\>\='
t_LTE    = r'\<\='
t_GT     = r'\>'
t_LT     = r'\<'
t_EQ     = r'\='

t_COMMA  = r'\,'

t_LPAREN = r'\('
t_RPAREN = r'\)'

t_LBRACKET = r'\['
t_RBRACKET = r'\]'

t_LBRACE = r'\{'
t_RBRACE = r'\}'

# floating point number
def t_FLOAT(t):
    r'-?\d+\.\d*(e-?\d+)?'
    t.value = float(t.value)
    return t

# integer
def t_INT(t):
    r'-?\d+'
    t.value = int(t.value)
    return t

# boolean value
def t_BOOL(t):
    r'true|false|True|False'
    if t.value.lower() == "true":
        t.value = True
    else:
        t.value = False
    return t

# identifier
def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.value = Id(t.value)
    return t

# string
# Read in a string, as in C.  
# The following backslash sequences have their usual special meaning:
#  \", \\, \n, and \t.
def t_STRING(t):
    r'\"([^\\"]|(\\.))*\"'
    escaped = 0
    str = t.value[1:-1]
    new_str = ""
    for i in range(0, len(str)):
        c = str[i]
        if escaped:
            if c == "n":
                c = "\n"
            elif c == "t":
                c = "\t"
            new_str += c
            escaped = 0
        else:
            if c == "\\":
                escaped = 1
            else:
                new_str += c
    t.value = new_str
    return t

t_ignore = " \t"

def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

# Build the lexer
lex.lex()

# Adding precedence rules
precedence = (
    ('left', 'PLUS', 'MINUS'),
    ('left', 'MULT', 'EXP', 'EXP'),
    ('right', 'EQ', 'LT', 'GT', 'LTE', 'GTE')
)

# Parsing rules
def p_expr(t):
    """
    expr : binary_expr
         | unary_expr
         | var
         | func
         | assign
         | decomp
    """
    t[0] = t[1]

def p_expr_group(t):
    """
    expr : LPAREN expr RPAREN
    """
    t[0] = t[2]

def p_binary_expr(t):
    """
    binary_expr : expr PLUS  expr
                | expr MINUS expr
                | expr MULT  expr
                | expr EXP   expr
                | expr GTE   expr
                | expr LTE   expr
                | expr GT    expr
                | expr LT    expr
                | expr EQ    expr
    """
    t[0] = FuncCall(t[2],[t[1],t[3]])

def p_unary_expr(t):
    """
    unary_expr  : MINUS expr
    """
    t[0] = FuncCall(t[1],[t[2]])

def p_func(t):
    """
    func : ID LPAREN args RPAREN
         | ID LPAREN RPAREN
    """
    if t[2] == ")":
        t[0] = FuncCall(t[1])
    else:
        t[0] = FuncCall(t[1], t[3])

def p_var(t):
    """
    var : const
        | ID
    """
    t[0] = t[1]

def p_const(t):
    """
    const : INT
          | FLOAT
          | BOOL
          | STRING
    """
    t[0] = Constant(t[1])

def p_assign(t):
    """
    assign : ID EQ expr
    """
    vmaps[t[1]] = t[3]
    t[0] = t[3]

def p_decomp(t):
    """
    decomp : expr LBRACKET const RBRACKET
    """
    t[0] = FuncCall("decompose",[t[1],t[3]])

def p_args_extend(t):
    """
    args : args COMMA expr
    """
    t[0] = t[1] + [t[3]]

def p_args_expr(t):
    """
    args : expr
    """
    t[0] = [t[1]]

def p_error(p):
    if p:
        print("Syntax error at '%s'" % p.value)

# Build the parser
yacc.yacc()

def parse(s):
    """
    Main entry point for parsing from outside of this module.
    """
    global vmaps
    vmaps = {}
    res = yacc.parse(s)
    print "VMaps = ", vmaps
    # TODO: return vmaps as well
    # so it can be used for flow gen
    #return res, vmaps
    return res

if __name__ == "__main__":
    if len(sys.argv) > 1:
        args = sys.argv[1:]
        for arg in args:
            print parse(arg)



