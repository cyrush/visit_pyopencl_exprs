#
# ${disclaimer}
#
"""
 file: common.py
 author: Cyrus Harrison <cyrush@llnl.gov>
 created: 4/9/2010
 description:
    Common utilities.

"""

import sys
import subprocess
import log


def sexe(cmd,ret_output=False,echo = False):
    """
    Helper for executing shell commands.
    """
    if echo:
        log.info("[exe: %s]" % cmd)
    if ret_output:
        p = subprocess.Popen(cmd,
                             shell=True,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)
        res =p.communicate()[0]
        return p.returncode,res
    else:
        return subprocess.call(cmd,shell=True)
