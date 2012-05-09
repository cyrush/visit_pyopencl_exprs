#
# ${disclaimer}
#
"""
 file: __init__.py
 author: Cyrus Harrison <cyrush@llnl.gov>
 created: 10/14/2010
 description:
    Init for 'flow.filters'.

"""

import cmd
import file_ops
# requires install of imagemagick command line tools.
import imagick

# check for import error only ...
try:
    # requires numpy
    import npy_ops
except:
    pass

# check for import error only ...
try:
    # requires pyopencl
    import pyocl_ops
    import pyocl_compile
except:
    pass
