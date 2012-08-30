#
import sys
sys.path.append("build/lib")
import flow
expr = open(sys.argv[1]).read()
stmts   = flow.Parser.parse(expr)
for s in stmts:
    print s
filters = flow.Generator.parse_network(expr)
for f in filters:
    print f