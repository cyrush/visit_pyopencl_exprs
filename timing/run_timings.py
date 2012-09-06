#!/usr/bin/env python
#
# ${disclaimer}
#
"""
 file: run__timings.py
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

def vcmd(nprocs=1,method='srun',tstride=1):
    if nprocs == 1:
        return "visit -nowin -timing -timing-processor-stride %d -cli -s" % (tstride)
    else:
        return "visit -l %s -np %d -nowin -timing -timing-processor-stride %d -cli -s" % (method,nprocs,tstride)

def setup_python_path():
    std_dir      = pjoin(sdir,"..","py-site-packages","lib","python2.6","site-packages")
    flow_dir     = pjoin(sdir,"..","flow","build","lib")
    flow_vpe_dir = pjoin(sdir,"..","visit_flow_vpe","build","lib")
    ppath = ""
    if "PYTHONPATH" in os.environ:
        ppath = os.environ["PYTHONPATH"] + ":"
    ppath += std_dir + ":" + flow_dir + ":" + flow_vpe_dir
    os.environ["PYTHONPATH"] = ppath
    fdir = pjoin(sdir,"..","flow")
    vdir = pjoin(sdir,"..","visit_flow_vpe")
    sexe("cd %s && visit -noconfig -nowin -cli -s setup.py build;" % fdir)
    sexe("cd %s && visit -noconfig -nowin -cli -s setup.py build;" % vdir)

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
    paths["pyocl_compile"] = pjoin(rdir,"pyocl_compile")
    paths["pyocl_ops"]     = pjoin(rdir,"pyocl_ops")
    paths["pyocl_batch"]   = pjoin(rdir,"pyocl_batch")
    os.mkdir(rdir)
    os.mkdir(paths["cpu"])
    os.mkdir(paths["hand"])
    os.mkdir(paths["pyocl_compile"])
    os.mkdir(paths["pyocl_ops"])
    os.mkdir(paths["pyocl_batch"])
    return paths

def prep_dest_dir(dest_dir):
    if os.path.isdir(dest_dir):
        shutil.rmtree(dest_dir)
    os.mkdir(dest_dir)
    
def expr_path(sdir,rtype):
    if rtype.count("vort"):
        expr = "ex_vort_mag.txt"
    elif rtype.count("mag"):
        expr = "ex_vel_mag.txt"
    else:
        expr = "ex_q_criteron.txt"
    return pjoin(sdir,"..",expr)

def test_script(*args):
    return os.path.abspath(pjoin(*args))

def exe_cpu(rtype,method,idx,rdirs,test_file,nprocs,ts):
    dest_dir = pjoin(rdirs["cpu"],"timing.results.%04d") % idx
    prep_dest_dir(dest_dir)
    if rtype.count("vort"):
        script = test_script(sdir,"..","standalone","vorticity","visit_vorticity_exec.py")
    elif rtype.count("mag"):
        script = test_script(sdir,"..","standalone","vector_mag","visit_vector_mag_exec.py")
    else:
        script = test_script(sdir,"..","standalone","q_criterion","visit_q_criterion_exec.py")
    print "\nEXEC:CPU\n   Dset:%s\n   Script:%s\n" % (test_file,test_script)
    cmd  = "cd %s && " % dest_dir
    cmd += vcmd(nprocs,method,tstride=ts) + " %s %s -save" % (test_script,test_file)
    cmd += " > run.out.txt"
    sexe(cmd)

def exe_gpu_hand(rtype,method,idx,rdirs,test_file,nprocs,ts):
    dest_dir = pjoin(rdirs["hand"],"timing.results.%04d") % idx
    prep_dest_dir(dest_dir)
    if rtype.count("vort"):
        script = test_script(sdir,"..","standalone","vorticity","visit_pyopencl_vorticity_exec.py")
    elif rtype.count("mag"):
        script = test_script(sdir,"..","standalone","vector_mag","visit_pyopencl_vector_mag_exec.py")
    else:
        script = test_script(sdir,"..","standalone","q_criterion","visit_pyopencl_q_criterion_exec.py")
    print "\nEXEC:GPU HAND\n   Dset:%s\n   Script:%s\n" % (test_file,script)
    cmd  = "cd %s && " % dest_dir
    cmd += vcmd(nprocs,method,tstride=ts) + " %s %s -save" % (script,test_file)
    cmd += " > run.out.txt"
    sexe(cmd)

def exe_flow(rtype,method,idx,rdirs,test_file,nprocs,ts,fset):
    dest_dir = pjoin(rdirs[fset],"timing.results.%04d") % idx
    prep_dest_dir(dest_dir)
    test_expr = expr_path(sdir,rtype)
    print "\nEXEC: %s\n   Dset:%s\n   Script:%s\n" % (fset,test_file,test_expr)
    cmd  = "cd %s && " % dest_dir
    script = test_script(sdir,"..","visit_flow_vpe","visit_exec_example_workspace.py")
    cmd += vcmd(nprocs,method,tstride=ts) + " %s %s %s %s -save" % (script,
                                                                    test_expr,
                                                                    test_file,
                                                                    fset)
    cmd += " > run.out.txt"
    sexe(cmd)
    dest_dir = pjoin(rdirs[fset],"timing.results.%04d") % idx

def exe_gpu_auto(rtype,method,idx,rdirs,test_file,nprocs,ts):
    exe_flow(rtype,method,idx,rdirs,test_file,nprocs,ts,"pyocl_compile")

def exe_gpu_batch(rtype,method,idx,rdirs,test_file,nprocs,ts):
    exe_flow(rtype,method,idx,rdirs,test_file,nprocs,ts,"pyocl_batch")

def exe_gpu_naive(rtype,method,idx,rdirs,test_file,nprocs,ts):
    exe_flow(rtype,method,idx,rdirs,test_file,nprocs,ts,"pyocl_ops")


def exe_single(rtype,method,test_file,idx,rdirs,nprocs,ts):
    #exe_gpu_hand(rtype,method,idx,rdirs,test_file,nprocs,ts)
    #exe_cpu(rtype,method,idx,rdirs,test_file,nprocs,ts)
    exe_gpu_auto(rtype,method,idx,rdirs,test_file,nprocs,ts)
    exe_gpu_batch(rtype,method,idx,rdirs,test_file,nprocs,ts)
    exe_gpu_naive(rtype,method,idx,rdirs,test_file,nprocs,ts)

def timing_summary(rdirs,nprocs,ofile = None):
    if not ofile is None:
        ofile = open(ofile,"w")
    for k,v in rdirs.items():
        vals = {}
        eefs = []
        tots = []
        base_out  = glob.glob(pjoin(v,"timing.results.*","run.out.txt"))
        for b in base_out:
            res,flow,ste,qte = fetch_base_timing_info(b)
        print res
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

def fetch_base_timing_info(f):
    res =""
    lines = open(f).readlines()
    for l in lines:
        if l.count("FlowExecExpr::TimingInfo  exe_flow") == 1:
            flow  = float(l.split()[-2].strip())
            res += "  exe_flow (host) = %s\n" % str(flow)
        if l.count("FlowExecExpr::TimingInfo  ctx_ste =") == 1:
            ste  = float(l.split()[-1].strip())
            res += "  ctx_ste (dev)   = %s\n" % str(ste)
        if l.count("FlowExecExpr::TimingInfo  ctx_qte =") == 1:
            qte  = float(l.split()[-1].strip())
            res += "  ctx_qte (dev)   = %s\n" % str(qte)
    return res,flow,ste,qte


if __name__ == "__main__":
    ntests = 1
    nprocs = 1
    test_file =pjoin(sdir,"..","rt3d_one_chunk.silo")
    args    = sys.argv
    rtype   = "vort"
    method  = "srun"
    tstride = 1
    if len(args) > 1:
        method = args[1]
    if len(args) > 2:
        test_file = os.path.abspath(args[2])
    if len(args) > 3:
        rtype = args[3]
    tag = rtype
    if len(args) > 4:
        ntests = int(args[4])
    if len(args) > 5:
        nprocs = int(args[5])
    if len(args) > 6:
        tag = tag  + args[6]
    if len(args) > 7:
        tstride = int(args[7])
    ofile = "out." + tag + ".txt" 
    setup_python_path()
    rdirs = prep_results_dir(tag)
    print "[executing %d timing runs]" % ntests
    for idx in xrange(ntests):
        exe_single(rtype,method,test_file,idx,rdirs,nprocs,tstride)
    print "[results]"
    timing_summary(rdirs,nprocs,ofile )



