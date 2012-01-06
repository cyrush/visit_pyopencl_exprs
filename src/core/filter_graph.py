#!/usr/bin/env python
#
# ${disclaimer}
#
"""
 file: filter_graph.py
 author: Cyrus Harrison <cyrush@llnl.gov>
 created: 10/14/2010
 description:
    TODO

"""

from property_tree import *
from Queue import Queue

class InvalidPortError(Exception):
    def __init__(self,port):
        self.port = port
    def __str__(self):
        return "Invalid port: '%s'" % self.port

class UnknownFilterNodeError(Exception):
    def __init__(self,node_name):
        self.name = node_name
    def __str__(self):
        return "Unknown filter node: '%s'" % self.name

class UnregisteredFilterTypeError(Exception):
    def __init__(self,type_name):
        self.type_name = type_name
    def __str__(self):
        return "Unknown filter type: '%s'" % self.name

class Filter(object):
    @classmethod
    def info(cls):
        res  = "Filter Type = %s\n" % cls.name
        res += "Input names = %s\n" % str(cls.inputs)
        res += "Default Params:%s\n" % str(cls.default_params)
        res += "Creates output: %s\n" % str(cls.output)
        return res

class FilterNode(object):
    def __init__(self,fname,ftype):
        self.name   = fname
        self.ftype  = ftype
        self.params = PropertyTree(init=self.ftype.default_params)
        self.produces_output = self.ftype.output
        self.number_of_ports = len(self.ftype.inputs)
        self.ports = self.ftype.inputs
        self.port_map = {}
        for port in self.ftype.inputs:
            self.port_map[port] = None
    def set_params(self,params):
        self.params.update(params)
    def __getitem__(self,path):
        return self.params[path]
    def __setitem__(self,path,obj):
        self.params[path] = obj
    def __str__(self):
        return "%s(%s)" % (self.name, self.ftype.name)

class FilterConnection(object):
    def __init__(self,src_node,des_node,port_name):
        self.src  = src_node
        self.des  = des_node
        self.port = port_name

class FilterGraph(object):
    def __init__(self):
        self.types = {}
        self.nodes = {}
        self.edges_out = {}
        self.edges_in  = {}
        self.node_count = -1
    def register_filter(self,filter_type):
        self.types[filter_type.name] = filter_type
    def connect(self,src_name,des_name,port_name):
        # special case for direct access to registry
        reg_src = (src_name[0] == ":")
        if not reg_src:
            src_node = self.nodes[src_name]
        else:
            src_node = src_name
        des_node = self.nodes[des_name]
        if not port_name in des_node.ports:
            raise InvalidPortError(port_name)
        fc = FilterConnection(src_node,des_node,port_name)
        self.edges_in[des_name][port_name] =  fc
        if not reg_src:
            self.edges_out[src_name].append(fc)
        des_node.port_map[port_name] = src_name
    def has_node(self,node_name):
        """
        Checks if a filter with the given name lives in the graph.
        """
        return node_name in self.nodes.keys()
    def add_node(self,type_name,node_name=None, node_params = None):
        """
        Adds a new instance of the filter with given type to the graph.
        """
        if not type_name in self.types:
            raise UnregisteredFilterTypeError(type_name)
        if node_name is None or self.has_node(node_name):
            node_name = self.__next_node_name(type_name)
            while self.has_node(node_name):
                node_name  = self.__next_node_name(type_name)
        node = FilterNode(node_name,self.types[type_name])
        if not node_params is None:
            node.set_params(node_params)
        # add node to the appropriate edge maps
        if node.number_of_ports > 0:
            self.edges_in[node.name] = {}
            for port in node.ports:
                self.edges_in[node.name][port] = None
        if node.produces_output:
            self.edges_out[node.name] = []
        self.nodes[node.name] = node
        return node
    def remove_node(self,inst_name):
        # make sure we have a node with the given name
        if not self.has_node(inst_name):
            raise UnknownFilterNodeError(inst_name)
        # get the node
        node = self.nodes[inst_name]
        # clean up any edges
        if node.number_of_ports > 0:
            del self.edges_in[inst_name]
        if node.produces_output:
            del self.edges_out[inst_name]
        del self.nodes[inst_name]
    def __str__(self):
        res = "FilterGraph:\nRegistered Filter Types:\n"
        for t in self.types.values():
            res += " " + str(t)  + "\n"
        res += "Active Filter Nodes:\n"
        for n in self.nodes.values():
            res += " " + str(n) + "\n"
        return res
    def __next_node_name(self,ftype=""):
        self.node_count += 1
        res = "filter"
        if ftype != "":
            res += "_%s" % ftype
        res += "_%04d" % self.node_count
        return res





