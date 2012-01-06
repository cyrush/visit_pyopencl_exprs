#!/usr/bin/env python
#
# ${disclaimer}
#
"""
 file: workspace.py
 author: Cyrus Harrison <cyrush@llnl.gov>
 created: 10/14/2010
 description:
    TODO

"""

import sys
import os
import imp
import hashlib
from registry import *
from filter_graph import *

def define_module(module_name,module_script,parent_dict=None):
    if module_name in sys.modules:
        module = sys.modules[module_name]
    else:
        module = imp.new_module(module_name)
        sys.modules[module_name] = module
        module.__file__ = "<%s>" % module_name
        module.__loader = None
    exec(module_script,module.__dict__,module.__dict__)
    if not parent_dict is None:
        parent_dict[module_name] = __input__(module_name)
    return module

class Workspace(object):
    def __init__(self):
        self.g = FilterGraph()
        self.r = Registry()
        self.filters = {}
    def register_filters(self,filter_module):
        for f in filter_module.filters:
            self.g.register_filter(f)
            self.filters[f.name] = f
    def add(self,filter_type,name = None, props= None):
        return self.g.add_node(filter_type,name,props)
    def connect(self,src_name,*des_filters):
        for d in des_filters:
            des,port = d.split(":")
            self.g.connect(src_name,des,port)
    def remove(self,filter_name):
        return self.remove_node(filter_name)
    def registry_add(self,key,obj,uref=-1):
        return self.r.add_entry(key,obj,uref)
    def registry_fetch(self,node_name):
        return self.r.fetch_entry(node_name)
    def registry_clear(self):
        return self.r.clear()
    def registry_keys(self):
        return self.r.keys()
    def registry_sources(self):
        return self.g.registry_sources()
    def execute(self):
        plan = ExecutionPlan(self.g)
        print "[Workspace Execute]\n%s" % str(plan)
        return self.__execute_plan(plan)
    def __execute_plan(self,plan):
        rval = None
        for t in plan.traversals:
            for v in t:
                # get filter node & # of refs
                node_name, uref = v
                node = self.g.nodes[node_name]
                print "[Workspace Execute Filter: %s(%s)]" % (node_name,node.ftype.name)
                # create filter instance
                node_cls = self.filters[node.ftype.name]
                # get inputs from registry
                inputs = {}
                for port,src_name in node.port_map.items():
                    if src_name[0] == ":":
                        src_name = src_name[1:]
                    inputs[port] = self.r.fetch_entry(src_name)
                # execute the filter with given settings
                res = node_cls.execute(node.name,inputs,node.params)
                # if output exists, place in registry
                if not res is None:
                    self.r.add_entry(node.name,res,uref)
                    rval = res
                print "[Workspace Registry Result]\n%s" % str(self.r)
        return rval
    @classmethod
    def load_workspace_script(cls,src=None,file=None):
        if src is None and not filename is None:
            print "[loading workingspace from: %s]" % os.path.abspath(file)
            src = open(file).read()
        module_name = hashlib.md5(src).hexdigest()
        res = define_module(module_name,src)
        # setup the workspace
        w = res.setup_workspace()
        return w;

class ExecutionPlan(object):
    def __init__(self,g):
        self.traversals = []
        self.untouched  = []
        # find sink points
        snks = []
        for node in g.nodes.values():
            if not node.produces_output or len(g.edges_out[node.name]) == 0:
                snks.append(node.name)
        tags = {}
        for name in g.nodes.keys():
            tags[name] = 0
        # execute bf traversals from each snk
        for snk_name in snks:
            trav  = []
            q = Queue()
            q.put(snk_name)
            while not q.empty():
                node_name = q.get()
                if tags[node_name] == 0:
                    uref = 1
                    node = g.nodes[node_name]
                    if node.produces_output:
                        uref = max(1,len(g.edges_out[node_name]))
                    if node.number_of_ports > 0:
                        for port,conn in g.edges_in[node_name].items():
                            if not conn is None:
                                # keep reg sources out of the queue
                                if conn.src.name[0] != ":":
                                    src_name = conn.src.name
                                    q.put(src_name)
                            else:
                                uref = 0
                    if uref > 0:
                        trav.append((node_name, uref ))
                        tags[node_name] = 1
            if len(trav) > 0:
                trav.reverse()
                self.traversals.append(trav)
            self.untouched = []
            for name, tag in tags.items():
                if tag == 0:
                    self.untouched.append(name)
    def __str__(self):
        ntrav = 0
        res = "Execution Plan:\n# of Traversals = %d"  % len(self.traversals)
        for trav in self.traversals:
            res += "\n Traversal %d:\n" % ntrav
            for node_name,uref in trav:
                res += "  %s (%d)\n"  %(node_name,uref)
            res += "\n"
            ntrav +=1
        nut = 0
        res += "# of Untouched Filter Nodes = %d" % len(self.untouched)
        if  len(self.untouched) > 0:
            res += " Untouched Filter Nodes:\n"
        for node_name in self.untouched:
                res += "  %s\n"  %(node_name)
        return res