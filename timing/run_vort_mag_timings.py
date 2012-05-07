#!/usr/bin/env python
#
# ${disclaimer}
#
"""
 file: run_vort_mag_timings.py
 author: Cyrus Harrison <cyrush@llnl.gov>
 description:
  Runs vort mag cases and organizes / reports timing output info.

"""

import sys
import subprocess
import os
import shutil
import glob
from os.path import join as pjoin

sdir = os.path.split(os.path.abspath(__file__))[0]

def sexe(cmd):
    print "[exe: %s]" % cmd
    subprocess.call(cmd,shell=True)

def vcmd(nprocs=1):
    if nprocs == 1:
        return "visit -nowin -timing -cli -s"
    else:
        return "visit -l srun -np %d -nowin -timing -cli -s" % nprocs

def setup_python_path():
    flow_dir     = pjoin(sdir,"..","flow","build","lib")
    flow_vpe_dir = pjoin(sdir,"..","visit_flow_vpe","build","lib")
    ppath = ""
    if "PYTHONPATH" in os.environ:
        ppath = os.environ["PYTHONPATH"] + ":"
    ppath += flow_dir + ":" + flow_vpe_dir
    print ppath
    os.environ["PYTHONPATH"] = ppath
    sexe("cd ../flow && visit -noconfig -nowin -cli -s setup.py build;")
    sexe("cd ../visit_flow_vpe && visit -noconfig -nowin -cli -s setup.py build;")

def prep_results_dir(tag):
    if tag is None:
        rdir = os.path.abspath("_timing_results")
    else:
        rdir = os.path.abspath("_%s_timing_results" % tag)
    paths = {}
    if os.path.isdir(rdir):
        shutil.rmtree(rdir)
    paths["root"] = rdir 
    paths["cpu"]  = pjoin(rdir,"cpu.visit")
    paths["hand"] = pjoin(rdir,"gpu.hand.coded")
    paths["auto"] = pjoin(rdir,"gpu.auto.gen")
    paths["naive"] = pjoin(rdir,"gpu.naive")
    os.mkdir(rdir)
    os.mkdir(paths["cpu"])
    os.mkdir(paths["hand"])
    os.mkdir(paths["auto"])
    os.mkdir(paths["naive"])
    return paths

def move_results(dest_dir):
    os.mkdir(dest_dir)
    cmd = "mv *.timings %s" % dest_dir
    sexe(cmd)
    cmd = "mv chunk*.png %s" % dest_dir
    sexe(cmd)


def exe_cpu(idx,rdirs,test_file,nprocs):
    test_script = pjoin(sdir,"..","standalone","vorticity","visit_vorticity_exec.py")
    cmd = vcmd(nprocs) + " %s %s -save" % (test_script,test_file)
    sexe(cmd)
    dest_dir = pjoin(rdirs["cpu"],"timing.results.%04d") % idx
    move_results(dest_dir)

def exe_gpu_hand(idx,rdirs,test_file,nprocs):
    test_script = pjoin(sdir,"..","standalone","vorticity","visit_pyopencl_vorticity_exec.py")
    cmd = vcmd(nprocs) + " %s %s -save" % (test_script,test_file)
    sexe(cmd)
    dest_dir = pjoin(rdirs["hand"],"timing.results.%04d") % idx
    move_results(dest_dir)

def exe_gpu_auto(idx,rdirs,test_file,nprocs):
    test_script = pjoin(sdir,"..","visit_flow_vpe","visit_exec_example_workspace.py")
    test_wspace = pjoin(sdir,"..","visit_flow_vpe","examples","flow_vpe_pyocl_compile_vort_mag_1.py")
    cmd = vcmd(nprocs) + " %s %s %s -save" % (test_script,test_wspace,test_file)
    sexe(cmd)
    dest_dir = pjoin(rdirs["auto"],"timing.results.%04d") % idx
    move_results(dest_dir)

def exe_gpu_naive(idx,rdirs,test_file,nprocs):
    test_script = pjoin(sdir,"..","visit_flow_vpe","visit_exec_example_workspace.py")
    test_wspace = pjoin(sdir,"..","visit_flow_vpe","examples","flow_vpe_pyocl_ops_vort_mag_1.py")
    cmd = vcmd(nprocs) + " %s %s %s -save" % (test_script,test_wspace,test_file)
    sexe(cmd)
    dest_dir = pjoin(rdirs["naive"],"timing.results.%04d") % idx
    move_results(dest_dir)

def exe_single(test_file,idx,rdirs,nprocs):
    exe_gpu_hand(idx,rdirs,test_file,nprocs)
    exe_cpu(idx,rdirs,test_file,nprocs)
    exe_gpu_auto(idx,rdirs,test_file,nprocs)
    exe_gpu_naive(idx,rdirs,test_file,nprocs)

def timing_summary(rdirs,nprocs):
    for k,v in rdirs.items():
        vals = {}
        eefs = []
        tots = []
        if nprocs == 1:
            fs = glob.glob(pjoin(v,"timing.results.*","engine_ser.timings"))
        else:
            fs = glob.glob(pjoin(v,"timing.results.*","engine_par.*timings"))
        if len(fs) > 0:
            print "%s:" % k
            for f in fs:
                txt,eef,tot = fetch_timing_info(f)
                print txt
                eefs.append(eef)
                tots.append(tot)
            print " eef_avg = %s" % str(sum(eefs)/float(len(eefs)))
            print " tot_avg = %s" % str(sum(tots)/float(len(tots)))

def fetch_timing_info(f):
    res =""
    lines = open(f).readlines()
    eef = -1
    tot = -1
    for l in lines:
        if l.count("avtExpressionEvaluatorFilter took ") == 1:
            eef  = float(l.split()[-1].strip())
            res += "  eef   = %s\n" % str(eef)
        if l.count("Total component run time took") == 1:
            tot  = float(l.split()[-1].strip())
            res += "  total = %s\n" % str(tot)
    return res,eef,tot

if __name__ == "__main__":
    ntests = 1
    nprocs = 1
    tag = None
    test_file =pjoin(sdir,"..","rt3d_small_chunk.silo")
    test_file =pjoin(sdir,"..","rt3d_one_chunk.silo")
    test_file =pjoin(sdir,"..","single_large_test_with_coords.silo")
    args = sys.argv
    if len(args) > 1:
        ntests = int(args[1])
    if len(args) > 2:
        test_file = os.path.abspath(args[2])
    if len(args) > 3:
        nprocs = int(args[3])
    if len(args) > 4:
        tag = args[4]
    setup_python_path()
    rdirs = prep_results_dir(tag)
    print "[executing %d timing runs]" % ntests
    for idx in xrange(ntests):
        exe_single(test_file,idx,rdirs,nprocs)
    print "[results]"
    timing_summary(rdirs,nprocs)



