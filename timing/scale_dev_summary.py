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
    res["dev_tot_all"] = []
    for r in runs:
        lines = open(pjoin(r,"run.out.txt")).readlines()
        rvals = {}
        res["runs"].append(rvals)
        dtota = 0.0
        for l in lines:
            if l.count("{'ste") > 0:
                lproc = l.strip().replace("'",'"').replace("L","")
                rdct = json.loads(lproc)
                rvals[rdct["tag"]] = rdct
                if rdct["tag"] == "win":
                    dtota += rdct["ste"]
                    res["avg_win_ste"] += rdct["ste"]
                if rdct["tag"] == "rout":
                    dtota += rdct["ste"]
                    res["avg_rout_ste"] += rdct["ste"]
                if rdct["tag"] == "kexec":
                    dtota += rdct["ste"]
                    res["avg_kexec_ste"] += rdct["ste"]
                if rdct["tag"] == "total":
                    rv =  rdct["dev_max_alloc"]
                    if rv > res["dev_max_alloc"] : res["dev_max_alloc"]  = rv
        res["dev_tot_all"].append(dtota)
    for k in res.keys():
        if k.count("avg_"):
            res[k] = res[k] / float(len(runs))
    res["dev_tot_all"].sort()
    res["avg_dev_tot_all"] = sum(res["dev_tot_all"])  / float(len(res["dev_tot_all"]))
    res["dev_tot_clamp"] = res["dev_tot_all"][1:-1] 
    res["avg_dev_tot_clamp"] = sum(res["dev_tot_clamp"])  / float(len(res["dev_tot_clamp"]))
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
                win_ste = v["avg_win_ste"]
                rout_ste = v["avg_rout_ste"]
                ke_ste = v["avg_kexec_ste"]
                dt_ste   = v["avg_dev_tot_all"]
                dtc_ste  = v["avg_dev_tot_clamp"]
                print did,",", expr,",", csize,",", k, ",", win_ste ,",", rout_ste ,",", ke_ste ,",", dt_ste,",",dtc_ste, ",",v["dev_max_alloc"]
    

