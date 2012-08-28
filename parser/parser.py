#!/usr/bin/env python
#
# ${disclaimer}
#
"""
 file: visit_exprs_parser.py
 authors: Cyrus Harrison <cyrush@llnl.gov>
         Maysam Moussalem <maysam@tacc.utexas.edu>

 description:
  ply (python lex & yacc) parser for VisIt's expression language.
  I used Mayam's visit_exprs.py as a starting point & adapted a subset
  of rules from VisIt's existing expression language parser:
   http://portal.nersc.gov/svn/visit/trunk/src/common/expr/ExprGrammar.C

 I also used this following tutorial as a reference:
  http://drdobbs.com/web-development/184405580

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
import os

import ply.lex as lex
import ply.yacc as yacc


class FuncCall(object):
    def __init__(self,name,args=None):
        self.name = name
        self.args = args
    def __str__(self):
        if self.args is None:
            return "%s()" % (self.name)
        else:
            return "%s(%s)" % (self.name, str(self.args))
    def __repr__(self):
       return str(self)

class Assignment(object):
    def __init__(self,name,value):
        self.name = name
        self.value = value
    def __str__(self):
        return str(self.name) + " = " + str(self.value)
    def __repr__(self):
        return str(self)

class Constant(object):
    def __init__(self,value):
        self.value = value
    def __str__(self):
        return "Const(%s)" % str(self.value)
    def __repr__(self):
        return str(self)

class Identifier(object):
    def __init__(self,name):
        self.name = name
    def __str__(self):
        return "Id(" + str(self.name) + ")"
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
          'DIV',
          'EXP',
          'GTE',
          'LTE',
          'GT',
          'LT',
          'EQ',
          'ASSIGN',
          'COMMA',
          'LPAREN',
          'RPAREN',
          'LBRACKET',
          'RBRACKET',
          'LBRACE',
          'RBRACE',
          'SEMI',
          "NEWLINE"
          ]

t_PLUS   = r'\+'
t_MINUS  = r'-'
t_MULT   = r'\*'
t_DIV    = r'\\'
t_EXP    = r'\^'

t_GTE    = r'\>\='
t_LTE    = r'\<\='
t_GT     = r'\>'
t_LT     = r'\<'
t_EQ     = r'\=\='
t_ASSIGN = r'\='

t_COMMA  = r'\,'

t_LPAREN = r'\('
t_RPAREN = r'\)'

t_LBRACKET = r'\['
t_RBRACKET = r'\]'

t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_SEMI   = r'\;'


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
    t.value = Identifier(t.value)
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

def t_COMMENT(t):
    r'\#.*\n*'
    pass
    # No return value. Token discarded


# Define a rule so we can track line numbers
def t_NEWLINE(t):
    r'\n+'
    t.lexer.lineno += len(t.value)
    return t

def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

# Build the lexer
lex.lex()

# Parsing rules
# Adding precedence rules
precedence = (
    ('left', 'PLUS', 'MINUS'),
    ('left', 'MULT', 'DIV'),
    ('left', 'EXP'),
    ('right', 'EQ', 'LT', 'GT', 'LTE', 'GTE')
)

def p_statements(t):
    """
    statements : statements statement   
               | statement
    """
    if len(t) > 2:
        t[0] = t[1] + [t[2]]
    else:
        t[0] = [t[1]]
        
    
def p_statement(t):
    """ 
    statement : assign_expr NEWLINE
              | assign_expr SEMI NEWLINE
    """
    t[0] = t[1]

def p_statement_newline(t):
    """ 
    statement : NEWLINE
    """
    pass


def p_assign(t):
    """
    assign_expr : ID ASSIGN expr
    """
    t[0] = Assignment(t[1],t[3])

def p_expr(t):
    """
    expr : binary_expr
         | unary_expr
         | var
         | func
    """
    t[0] = t[1]

def p_binary_expr(t):
    """
    binary_expr : expr PLUS  expr
                | expr MINUS expr
                | expr MULT  expr
                | expr EXP   expr
                | expr DIV   expr
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
         | ID LBRACKET args RBRACKET
         | LBRACE args RBRACE
    """
    if t[2] == ")":
        t[0] = FuncCall(t[1])
    if t[1] == "{":
        t[0] = FuncCall("compose",t[2])
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
        print("Syntax error '%s'" % p.type)
        print("Syntax error at '%s'" % p.value)

# Build the parser
yacc.yacc()

def parse(s):
    """
    Main entry point for parsing from outside of this module.
    """
    return yacc.parse(s)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            txt = arg
            if os.path.isfile(arg):
                txt = open(arg).read()
            print "Parsing:\n" , txt, "\n"
            stmts = parse(txt)
            print "Result:"
            for r in stmts:
                print " ",r



