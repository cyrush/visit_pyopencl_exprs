#!/usr/bin/env python
#
# ${disclaimer}
#
"""
 file: registry.py
 author: Cyrus Harrison <cyrush@llnl.gov>
 created: 10/14/2010
 description:
    TODO

"""

class InvalidRegistryKey(Exception):
    def __init__(self,key):
        self.key = key
    def __str__(self):
        return "Invalid registry key: '%s'" % self.key

class RegistryEntry(object):
    def __init__(self,key,obj,uref):
        self.key     = key
        self.obj     = obj
        self.uref    = uref
    def __str__(self):
        res = "%s uref=%d" % (self.key,self.uref)
        if "nbytes" in dir(self.obj):
            res += " nbytes=%d" % self.obj.nbytes
        return res

class Registry(object):
    def __init__(self):
        self.entries = {}
    def add_entry(self,key,obj,uref=-1):
        print "[Registry add_entry: %s uref=%d]" % (key,uref)
        self.entries[key] = RegistryEntry(key,obj,uref)
    def fetch_entry(self,key):
        dfetch = False
        if key[0] == ":":
            dfetch = True
            key = key[1:]
        print "[Registry fetch_entry: %s]" % key
        # get obj from dict using key.
        # dec uref & if it equals zero remove it from the dict.
        # note: negative uref will live forever.
        if key in self.entries.keys():
            res = self.entries[key]
            if res.uref > 0 and dfetch == False:
                res.uref +=-1
                if res.uref == 0:
                    print "[Registry remove_entry: %s uref=0]" % key
                    del self.entries[key]
            return res.obj
        raise InvalidRegistryKey(key)
    def clear(self):
        self.entries = {}
    def keys(self):
        res = self.entries.keys()
        res.sort()
        return res
    def __str__(self):
        ekeys = self.entries.keys()
        ekeys.sort()
        res = "Registry Entries:\n"
        for ek in ekeys:
            re = self.entries[ek]
            res += " %s\n" % str(re)
        return res
