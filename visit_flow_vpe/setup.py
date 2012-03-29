#!/usr/bin/env python
#
# ${disclaimer}
#
"""
 file: setup_tests.py
 author: Cyrus Harrison <cyrush@llnl.gov>
 created: 3/28/2010
 description:
    distutils setup script for the 'visit_flow_vpe' module.

"""


from distutils.core import setup
import sys
import setup_tests


#
# Support running tests w/ visit's cli.
#
using_visit = False
try:
    # the command line string passed to cli
    # will confuse distutils, so modify
    # sys.argv to only have args passed after
    # '-s setup.py'
    args = Argv()
    sys.argv = [__file__]
    sys.argv.extend(args)
    using_visit = True
except:
    pass

setup(name='flow',
      version      ='0.1',
      author       = 'Cyrus Harrison',
      author_email = 'cyrush@llnl.gov',
      description  ='visit_flow_vpe',
      package_dir  = {'visit_flow_vpe':'src'},
      packages=['visit_flow_vpe'],
      package_data= { "visit_flow_vpe": ["*.vpe"]},
      cmdclass = { 'test': setup_tests.ExecuteTests})

if using_visit:
    sys.exit(0)