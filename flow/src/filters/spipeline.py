#*****************************************************************************
#
# Copyright (c) 2000 - 2012, Lawrence Livermore National Security, LLC
# Produced at the Lawrence Livermore National Laboratory
# LLNL-CODE-442911
# All rights reserved.
#
# This file is  part of VisIt. For  details, see https://visit.llnl.gov/.  The
# full copyright notice is contained in the file COPYRIGHT located at the root
# of the VisIt distribution or at http://www.llnl.gov/visit/copyright.html.
#
# Redistribution  and  use  in  source  and  binary  forms,  with  or  without
# modification, are permitted provided that the following conditions are met:
#
#  - Redistributions of  source code must  retain the above  copyright notice,
#    this list of conditions and the disclaimer below.
#  - Redistributions in binary form must reproduce the above copyright notice,
#    this  list of  conditions  and  the  disclaimer (as noted below)  in  the
#    documentation and/or other materials provided with the distribution.
#  - Neither the name of  the LLNS/LLNL nor the names of  its contributors may
#    be used to endorse or promote products derived from this software without
#    specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT  HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR  IMPLIED WARRANTIES, INCLUDING,  BUT NOT  LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND  FITNESS FOR A PARTICULAR  PURPOSE
# ARE  DISCLAIMED. IN  NO EVENT  SHALL LAWRENCE  LIVERMORE NATIONAL  SECURITY,
# LLC, THE  U.S.  DEPARTMENT OF  ENERGY  OR  CONTRIBUTORS BE  LIABLE  FOR  ANY
# DIRECT,  INDIRECT,   INCIDENTAL,   SPECIAL,   EXEMPLARY,  OR   CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT  LIMITED TO, PROCUREMENT OF  SUBSTITUTE GOODS OR
# SERVICES; LOSS OF  USE, DATA, OR PROFITS; OR  BUSINESS INTERRUPTION) HOWEVER
# CAUSED  AND  ON  ANY  THEORY  OF  LIABILITY,  WHETHER  IN  CONTRACT,  STRICT
# LIABILITY, OR TORT  (INCLUDING NEGLIGENCE OR OTHERWISE)  ARISING IN ANY  WAY
# OUT OF THE  USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH
# DAMAGE.
#*****************************************************************************
"""
 file: spipeline.py
 author: Cyrus Harrison <cyrush@llnl.gov>

 created: 2/4/2013
 description:
    Provides flow filters foundation for user defined script pipelines.

"""
import logging
#logging.basicConfig(level=logging.INFO)
logging.basicConfig(level=logging.ERROR)


import numpy as npy

from ..core import Filter, Context, log

def info(msg):
    log.info(msg,"filters.spipeline")

def err(msg):
    log.error(msg,"filters.spipeline")



class PythonUserScriptBaseFilter(Filter):
    def execute(self):
        inputs = [self.input(v) for v in self.input_ports]
        script_globals = {}
        script_locals  = {}
        # place input names in our env
        output_stub = "def setout(v): globals()['__out_val'] = v\n"
        for v in self.input_ports:
            script_globals[v] = self.input(v)
        exec(output_stub,script_globals,script_locals)
        exec(self.filter_source,script_globals,script_locals)
        return script_globals["__out_val"]

def UserScriptFilter(filter_name,filter_info):
    f = filter_info
    cname = "UserScriptFilter" +  filter_name[0].upper() + filter_name[1:]
    cdct =  {"filter_type":filter_name,
             "input_ports": f["vars"],
             "default_params": {},
             "output_port":  True,
             "filter_source": f["source"]}
    return type(str(cname),(PythonUserScriptBaseFilter,),cdct)
    #if f["runtime"] == "python":
    #   return type(cname,(PythonUserScriptBaseFilter,),cdct) 
    #else: # error, but we will support R
    #    pass

filters = []
def register_user_scripts(uscripts):
    for filter_name,filter_info in uscripts.items():
        filters.append(UserScriptFilter(filter_name,filter_info))

