#!/usr/bin/env python
#
# ${disclaimer}
#
"""
 file: single_node_scale.py
 author: Cyrus Harrison <cyrush@llnl.gov>
 description:
  TODO

"""

import sys
import subprocess
import socket
import os
import glob
import json
from os.path import join as pjoin


def proc_runs(runs):
    res = {}
    rts = []
    res["runs"] = rts
    res["avg_win_ste"]  = 0.0
    res["avg_kexec_ste"] = 0.0
    res["avg_rout_ste"] = 0.0
    res["dev_max_alloc"]  = 0
    for r in runs:
        lines = open(pjoin(r,"run.out.txt")).readlines()
        rvals = {}
        res["runs"].append(rvals)
        for l in lines:
            if l.count("{'ste") > 0:
                lproc = l.strip().replace("'",'"').replace("L","")
                rdct = json.loads(lproc)
                rvals[rdct["tag"]] = rdct
                if rdct["tag"] == "win":
                    res["avg_win_ste"] += rdct["ste"]
                if rdct["tag"] == "rout":
                    res["avg_rout_ste"] += rdct["ste"]
                if rdct["tag"] == "kexec":
                    res["avg_kexec_ste"] += rdct["ste"]
                if rdct["tag"] == "total":
                    rv =  rdct["dev_max_alloc"]
                    if rv > res["dev_max_alloc"] : res["dev_max_alloc"]  = rv
    for k in res.keys():
        if k.count("avg_"):
            res[k] = res[k] / float(len(runs))
    return res

def find_runs(base):
    res = {}
    rdir = os.path.split(base)[1]
    res["expr"] = rdir[1:rdir.find("_plat")]
    plat  = rdir[rdir.find("_plat")+6:rdir.find("_dev")]
    dev = rdir[rdir.find("_dev")+5:rdir.find("_ser")]
    chunk = rdir[rdir.find("_size")+6:rdir.find("_timing")]
    res["dev"]   = int(dev)
    res["plat"]  = int(plat)
    res["chunk"] = int(chunk)
    rcases = glob.glob(pjoin(base,"*"))
    res["cases"] = {}
    for r in rcases:
        cname = os.path.split(r)[1]
        cruns = glob.glob(pjoin(r,"timing.results.*"))
        cruns.sort()
        rx = proc_runs(cruns)
        res["cases"][cname] = rx
    return res

def main():
    args       = sys.argv
    res = []
    for arg in args[1:]:
        res.append(find_runs(os.path.abspath(arg)))
    return res

if __name__ == "__main__":
    rx = main()
    for r in rx:
        did   = "d_%d_%d" % (r["plat"],r["dev"])
        csize = r["chunk"]
        expr  = r["expr"]
        for k,v in r["cases"].items():
            if k.count("cpu")  == 0:
                print did,",", expr,",", csize,",", k, ",", v["avg_win_ste"],",",v["avg_rout_ste"],",",v["avg_kexec_ste"],",",v["dev_max_alloc"]
    

