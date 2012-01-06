#!/usr/bin/env python
#
# ${disclaimer}
#
"""
  file: setup.py
  author: Cyrus Harrison <cyrush@llnl.gov>

  distutils setup script for the 'flow' module.

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
      version='0.001a',
      author = 'Cyrus Harrison',
      author_email = 'cyrush@llnl.gov',
      description='Simple Data Flow',
      package_dir = {'flow':'src'},
      packages=['flow','flow.core','flow.interactive','flow.filters', 'flow.vpe'],
      package_data= { "flow": ["vpe/*.vpe"]},
      cmdclass = { 'test': setup_tests.ExecuteTests})

if using_visit:
    sys.exit(0)