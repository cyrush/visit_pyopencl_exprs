#!/usr/bin/env python
#
# ${disclaimer}
#
"""
 file: setup_tests.py
 author: Cyrus Harrison <cyrush@llnl.gov>
 created: 10/14/2010
 description:
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
      version      ='0.1',
      author       = 'Cyrus Harrison',
      author_email = 'cyrush@llnl.gov',
      description  ='flow: A small, flexible python data flow framework.',
      package_dir  = {'flow':'src'},
      packages=['flow','flow.core','flow.parser','flow.filters'],
      cmdclass = { 'test': setup_tests.ExecuteTests})

if using_visit:
    sys.exit(0)