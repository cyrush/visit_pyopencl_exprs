#
# file: setup.py
# author: Cyrus Harrison <cyrush@llnl.gov>
#
# distutils setup script for the 'visit_pyopencl_exprs' module.
#

from distutils.core import setup
import sys
import setup_tests


#
# Support build & install using VisIt's cli.
#
using_visit = False
try:
    # The command line string passed to cli
    # will confuse distutils, so modify
    # sys.argv to only have args passed after
    # '-s setup.py'
    args = Argv()
    sys.argv = [__file__]
    sys.argv.extend(args)
    using_visit = True
except:
    pass

setup(name='visit_pyopencl_exprs',
      version='0.001a',
      author = 'Cyrus Harrison',
      author_email = 'cyrush@llnl.gov',
      description='VisIt PyOpenCL Expressions Sandbox Module',
      package_dir = {'visit_pyopencl_exprs':'src'},
      packages=['visit_pyopencl_exprs'],
      cmdclass = { 'test': setup_tests.ExecuteTests})

if using_visit:
    sys.exit(0)