# -----------------------------------------------------------------------------
# Author: Maysam Moussalem (maysam@tacc.utexas.edu)
#
# Description: Python Lex-Yacc for VisIt PyOpenCL expressions.
#
# Usage: python visit_exprs.py
# -----------------------------------------------------------------------------

import sys, subprocess, os, math, numpy
sys.path.insert(0,"ply-3.4")

if sys.version_info[0] >= 3:
    raw_input = input

import ply.lex as lex
import ply.yacc as yacc

# Tokens
reserved = {'cos' : 'COS',
            'sin': 'SIN',
            'tan': 'TAN',
            'cosh': 'COSH',
            'sinh': 'SINH',
            'tanh': 'TANH',
            'arccos': 'ARCCOS',
            'arcsin': 'ARCSIN',
            'arctan': 'ARCTAN',
            'sqrt': 'SQRT',
            'ln': 'LN',
            'log': 'LOG',
            'eq': 'EQ',
            'neq': 'NEQ',
            'floor': 'FLOOR',
            'ceil': 'CEIL'}

tokens = ['VAR','NUMBER'] + list(reserved.values())

literals = ['=','+','-','*','/', '(',')', '%', '^', '<', '>']

def t_VAR(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value,'VAR')    # Check for reserved words
    return t

def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

t_ignore = " \t"

def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")
    
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)
    
# Build the lexer
lex.lex()

# Parsing rules

# dictionary of variable names
vars = { }

# Start with precedence rules
# They need to be ordered from lowest to highest precedence
# e.g. * and / have higher precedence than + and -
precedence = (
    ('left','+','-'),
    ('left','*','/', '%', '^'),
    ('right','UMINUS'),
    ('right', 'COS', 'SIN', 'TAN', 'COSH', 'SINH', 'TANH',
     'ARCCOS', 'ARCSIN', 'ARCTAN', 'SQRT', 'LN', 'LOG',
     'EQ', 'NEQ', 'FLOOR', 'CEIL')
    )

def p_statement_assign(p):
    'statement : VAR "=" expression'
    vars[p[1]] = p[3]

def p_statement_expr(p):
    'statement : expression'
    print(p[1])

def p_expression_binop(p):
    '''expression : expression '+' expression
                  | expression '-' expression
                  | expression '*' expression
                  | expression '/' expression
                  | expression '%' expression
                  | expression '^' expression'''
    if p[2] == '+'  : p[0] = p[1] + p[3]
    elif p[2] == '-': p[0] = p[1] - p[3]
    elif p[2] == '*': p[0] = p[1] * p[3]
    elif p[2] == '/': p[0] = p[1] / p[3]
    elif p[2] == '%': p[0] = p[1] % p[3]
    elif p[2] == '^': p[0] = p[1] ** p[3]

def p_expression_uminus(p):
    "expression : '-' expression %prec UMINUS"
    p[0] = -p[2]

def p_expression_group(p):
    "expression : '(' expression ')'"
    p[0] = p[2]

def p_expression_number(p):
    "expression : NUMBER"
    p[0] = p[1]

def p_expression_var(p):
    "expression : VAR"
    try:
        p[0] = vars[p[1]]
    except LookupError:
        print("Undefined variable '%s'" % p[1])
        p[0] = 0

def p_error(p):
    if p:
        print("Syntax error at '%s'" % p.value)
    else:
        print("Syntax error at EOF")

yacc.yacc()

while 1:
    try:
        s = raw_input('calc > ')
    except EOFError:
        break
    if not s: continue
    yacc.parse(s)

