#
# ${disclaimer}
#
"""
 file: management.py
 author: Cyrus Harrison <cyrush@llnl.gov>
 created: 8/30/2012
 description:
    TODO

"""

import sys

def module(name):
    mname = "flow.filters." + name
    if mname in sys.modules:
        return sys.modules[mname]

