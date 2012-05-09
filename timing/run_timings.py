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

def vcmd(nprocs=1,method='srun'):
    if nprocs == 1:
        return "visit -nowin -timing -cli -s"
    else:
        return "visit -l %s -np %d -nowin -timing -cli -s" % (method,nprocs)

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
    paths["root"]  = rdir
    paths["cpu"]   = pjoin(rdir,"cpu.visit")
    paths["hand"]  = pjoin(rdir,"gpu.hand.coded")
    paths["auto"]  = pjoin(rdir,"gpu.auto.gen")
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


def exe_cpu(rtype,idx,rdirs,test_file,nprocs):
    if rtype.count("vort"):
        test_script = pjoin(sdir,"..","standalone","vorticity","visit_vorticity_exec.py")
    elif rtype.count("mag"):
        test_script = pjoin(sdir,"..","standalone","vector_mag","visit_vector_mag_exec.py")
    else:
        test_script = pjoin(sdir,"..","standalone","q_criterion","visit_q_criterion_exec.py")
    cmd = vcmd(nprocs) + " %s %s -save" % (test_script,test_file)
    print "\nEXEC:CPU\n   Dset:%s\n   Script:%s\n" % (test_file,test_script)
    sexe(cmd)
    dest_dir = pjoin(rdirs["cpu"],"timing.results.%04d") % idx
    move_results(dest_dir)

def exe_gpu_hand(rtype,idx,rdirs,test_file,nprocs):
    if rtype.count("vort"):
        test_script = pjoin(sdir,"..","standalone","vorticity","visit_pyopencl_vorticity_exec.py")
    elif rtype.count("mag"):
        test_script = pjoin(sdir,"..","standalone","vector_mag","visit_pyopencl_vector_mag_exec.py")
    else:
        test_script = pjoin(sdir,"..","standalone","q_criterion","visit_pyopencl_q_criterion_exec.py")
    print "\nEXEC:GPU HAND\n   Dset:%s\n   Script:%s\n" % (test_file,test_script)
    cmd = vcmd(nprocs) + " %s %s -save" % (test_script,test_file)
    sexe(cmd)
    dest_dir = pjoin(rdirs["hand"],"timing.results.%04d") % idx
    move_results(dest_dir)

def exe_gpu_auto(rtype,idx,rdirs,test_file,nprocs):
    test_script = pjoin(sdir,"..","visit_flow_vpe","visit_exec_example_workspace.py")
    if rtype.count("vort"):
        test_wspace = pjoin(sdir,"..","visit_flow_vpe","examples","flow_vpe_pyocl_compile_vort_mag_1.py")
    elif rtype.count("mag"):
        test_wspace = pjoin(sdir,"..","visit_flow_vpe","examples","flow_vpe_pyocl_compile_vel_mag_1.py")
    else:
        test_wspace = pjoin(sdir,"..","visit_flow_vpe","examples","flow_vpe_pyocl_compile_q_criterion.py")
    cmd = vcmd(nprocs) + " %s %s %s -save" % (test_script,test_wspace,test_file)
    print "\nEXEC:GPU AUTO\n   Dset:%s\n   Script:%s\n" % (test_file,test_wspace)
    sexe(cmd)
    dest_dir = pjoin(rdirs["auto"],"timing.results.%04d") % idx
    move_results(dest_dir)

def exe_gpu_naive(rtype,idx,rdirs,test_file,nprocs):
    test_script = pjoin(sdir,"..","visit_flow_vpe","visit_exec_example_workspace.py")
    if rtype.count("vort"):
        test_wspace = pjoin(sdir,"..","visit_flow_vpe","examples","flow_vpe_pyocl_ops_vort_mag_1.py")
    elif rtype.count("mag"):
        test_wspace = pjoin(sdir,"..","visit_flow_vpe","examples","flow_vpe_pyocl_ops_vel_mag_1.py")
    else:
        test_wspace = pjoin(sdir,"..","visit_flow_vpe","examples","flow_vpe_pyocl_ops_q_criterion.py")
    cmd = vcmd(nprocs) + " %s %s %s -save" % (test_script,test_wspace,test_file)
    print "\nEXEC:GPU NAIVE\n   Dset:%s\n   Script:%s\n" % (test_file,test_wspace)
    sexe(cmd)
    dest_dir = pjoin(rdirs["naive"],"timing.results.%04d") % idx
    move_results(dest_dir)

def exe_single(rtype,test_file,idx,rdirs,nprocs):
    exe_gpu_hand(rtype,idx,rdirs,test_file,nprocs)
    exe_cpu(rtype,idx,rdirs,test_file,nprocs)
    exe_gpu_auto(rtype,idx,rdirs,test_file,nprocs)
    exe_gpu_naive(rtype,idx,rdirs,test_file,nprocs)

def timing_summary(rdirs,nprocs,ofile = None):
    if not ofile is None:
        ofile = open(ofile,"w")
    for k,v in rdirs.items():
        vals = {}
        eefs = []
        tots = []
        if nprocs == 1:
            fs = glob.glob(pjoin(v,"timing.results.*","engine_ser.timings"))
        else:
            fs = glob.glob(pjoin(v,"timing.results.*","engine_par.*timings"))
        if len(fs) > 0:
            txt = "%s:\n indiv cases\n" % k
            print txt
            if not ofile is None: ofile.write(txt + "\n")
            for f in fs:
                txt,eef,tot = fetch_timing_info(f)
                print txt
                if not ofile is None: ofile.write(txt + "\n")
                eefs.append(eef)
                tots.append(tot)
            eef_avg = "%s: eef_avg = %s" %(k,str(sum(eefs)/float(len(eefs))))
            tot_avg = "%s: tot_avg = %s" %(k, str(sum(tots)/float(len(tots))))
            print eef_avg
            print tot_avg
            if not ofile is None: ofile.write("\n%s\n%s\n" % (eef_avg,tot_avg))

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
    test_file =pjoin(sdir,"..","rt3d_small_chunk.silo")
    test_file =pjoin(sdir,"..","rt3d_one_chunk.silo")
    test_file =pjoin(sdir,"..","single_large_test_with_coords.silo")
    args = sys.argv
    rtype = "vort"
    if len(args) > 1:
        test_file = os.path.abspath(args[1])
    if len(args) > 2:
        rtype = args[2]
    tag = rtype
    if len(args) > 3:
        ntests = int(args[3])
    if len(args) > 4:
        nprocs = int(args[4])
    if len(args) > 5:
        tag = tag  + args[5]
    ofile = "out." + tag + ".txt" 
    setup_python_path()
    rdirs = prep_results_dir(tag)
    print "[executing %d timing runs]" % ntests
    for idx in xrange(ntests):
        exe_single(rtype,test_file,idx,rdirs,nprocs)
    print "[results]"
    timing_summary(rdirs,nprocs,ofile )



