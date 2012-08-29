#!/usr/bin/env python
#
# ${disclaimer}
#
"""
 file: test_parser.py
 author: Cyrus Harrison <cyrush@llnl.gov>
 created: 8/29/2012
 description:
    unittest test cases for parser front-end.

"""

import unittest
from flow import *

# uncomment for detailed exe info
#import logging
#logging.basicConfig(level=logging.INFO)

class TestParser(unittest.TestCase):
    def test_01_simple_expr(self):
        stmts = Parser.parse("vel_mag = sqrt(vx^2 + vy^2 + vz^2)")
        print ""
        for s in stmts:
            print s

if __name__ == '__main__':
    unittest.main()

