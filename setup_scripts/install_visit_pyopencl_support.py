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
 file: install_visit_pyopencl_support.py
 author: Cyrus Harrison <cyrush@llnl.gov>
 description:
  Installs pyopencl and all supporting modules (including numpy) into
  a VisIt install.

 usage:
 # via VisIt's cli
 >visit -nowin -cli -s install_visit_pyopencl_support.py <destination-dir>
 # via std python
 >python install_visit_pyopencl_support.py <destination-dir>
"""

import os
import sys
import subprocess
import shutil
import urllib
import tarfile
import zipfile

using_visit = False
try:
    import visit
    args = Argv()
    using_visit= True
except ImportError:
    args = sys.argv[1:]

from os.path import join as pjoin

def SetupError(Exception):
    """ Exception when for when something goes wrong. """
    def __init__(self,msg):
        super(SetupError,self).__init__()
        print msg

def sexe(cmd,echo=True):
    """ Shell command helper. """
    print "[exe: %s]"% cmd
    ret = subprocess.call(cmd,shell=True)
    if ret != 0:
        raise SetupError("Error with shell command: %s" % cmd)

def python_bin():
    """ Fetches the proper path to visit or python. """
    if using_visit:
        ret = subprocess.call("which visit",shell=True)
        if ret != 0:
            raise SetupError("VisIt is not in your env PATH.")
        # return visit cli as exe
        return "visit -nowin -cli -s"
    else:
        # return python exe
        return sys.executable

def check_for_existing_module(mod_name,mod_ver=None):
    """
    Checks if a python module is already installed.
    Provides an option to check module version  as well.
    """
    print "[checking for existing `%s' install]" % mod_name
    res = False
    try:
        mod = __import__(mod_name)
        cver = None
        if "__version__" in dir(mod):
            cver = mod.__version__
        elif "version" in dir(mod):
            cver = mod.version.VERSION_TEXT
        if not mod_ver is None:
            if not cver is None:
                res = cver >= mod_ver
            else:
                res = True
        else:
            res = True
        print "[found `%s' version: %s]" % (mod_name,cver)
    except:
        pass
    return res

def check_for_distribute_module(ver=None):
    """
    Special logic to check for the `distribute' module.
    """
    print "[checking for existing `distrubute' install]"
    res = False
    try:
        mod = __import__("setuptools")
        if "_distribute" in dir(mod):
            print "[found `distribute' version: %s]" % mod.__version__
            if not ver is None:
                res = mod.__version__ >= ver
            else:
                res = True
    except:
        pass
    return res

def patch_python_setup_file(fname,seed="\n\n"):
    """
    Patches a standard python module `setup.py' file
    so the module can be build with and installed into VisIt's cli.
    """
    __setup_pre_patch = """
import sys
try:
    import visit
    args = visit.Argv()
    sys.argv = [__file__]
    sys.argv.extend(args)
    using_visit = True
except:
    using_visit = False

"""
    __setup_post_patch = "\nif using_visit:\n  sys.exit(0)\n"
    path = os.path.abspath(fname)
    print '[patching python setup script: %s]' % path
    data = open(path).read()
    fout = open(path,"w")
    # place the visit setup magic after the first empty line
    idx = data.find(seed)
    if idx == -1:
        fout.write(__setup_pre_patch)
        fout.write(data)
    else:
        fout.write(data[:idx+len(seed)])
        fout.write(__setup_pre_patch)
        fout.write(data[idx+len(seed):])
    fout.write(__setup_post_patch)
    fout.close()

def prepare_build_dir():
    """
    Use `_build_pyopencl_support' directory to contain build files.
    """
    cdir = os.path.split(os.path.abspath(os.getcwd()))[1]
    if cdir != "_build_pyopencl_support":
        # work in subdir "_build"
        wpath = pjoin(os.getcwd(),"_build_pyopencl_support")
        print wpath
        if not os.path.isdir(wpath):
            os.mkdir(wpath)
        print "[using build directory: %s]" % wpath
        os.chdir(wpath)

def prepare_module_dest_dir(dest):
    """
    Setup proper directory structure to install python modules.
    """
    ddirs = [ ]
    ddirs.append(dest)
    ddirs.append(pjoin(ddirs[-1],"lib"))
    ddirs.append(pjoin(ddirs[-1],"python2.6"))
    ddirs.append(pjoin(ddirs[-1],"site-packages"))
    print ddirs
    for d in ddirs:
        if not os.path.isdir(d):
            print "[creating directory: %s]" % d
            os.mkdir(d)

def setup_numpy(dest_dir=None):
    """ Builds and installs numpy."""
    if check_for_existing_module("numpy"):
        print "[skipping build: `numpy' is already installed]"
        return
    prepare_build_dir()
    print "[preparing to build: `numpy' version: (github-trunk)]"
    # get numpy source
    if os.path.isdir("numpy"):
        print "[removing existing source dir: `numpy']"
        shutil.rmtree("numpy")
    npy_repo = "https://github.com/numpy/numpy.git"
    print "[cloning `numpy' github repo (%s)]" % npy_repo
    sexe('git clone %s' % npy_repo)
    patch_python_setup_file(pjoin("numpy","setup.py"),seed="import subprocess\n")
    print "[building + installing: `numpy']"
    cmd ="cd numpy; %s setup.py build " % python_bin()
    if os.environ.has_key("FCOMPILER"):
        cmd += "--fcompiler=%s " % os.environ["FCOMPILER"]
    sexe(cmd)
    cmd ="cd numpy; %s setup.py install" % python_bin()
    if not dest_dir is None:
        cmd += " --prefix %s" % dest_dir
    sexe(cmd)

def setup_pyopencl(dest_dir=None):
    """ Builds and installs pyopencl."""
    if check_for_existing_module("pyopencl"):
        print "[skipping build: `pyopencl' is already installed]"
        return
    prepare_build_dir()
    print "[preparing to build: `pyopencl' version: (git-trunk)]"
    # get numpy source
    if os.path.isdir("pyopencl"):
        print "[removing existing source dir: `pyopencl']"
        shutil.rmtree("pyopencl")
    pyocl_repo = "https://github.com/inducer/pyopencl"
    print "[cloning `pyopencl' git repo (%s)]" % pyocl_repo
    sexe('git clone %s' % pyocl_repo)
    sexe('cd pyopencl; git submodule init; git submodule update');
    patch_python_setup_file(pjoin("pyopencl","setup.py"))
    print "[building + installing: `pyopencl']"
    cmd ="cd pyopencl; %s setup.py build " % python_bin()
    cmd ="cd pyopencl; %s setup.py install" % python_bin()
    if not dest_dir is None:
        cmd += " --prefix %s" % dest_dir
    sexe(cmd)

def setup_pypi_package(pkg_name,pkg_ver,pkg_type="tar.gz",force=False,dest_dir=None):
    """ Builds and installs a package from pypi."""
    if not force:
        if  check_for_existing_module(pkg_name,pkg_ver):
            print "[skipping build: `%s' is already installed]" % pkg_name
            return
        print "[preparing to build: `%s' version: %s ]" % (pkg_name,pkg_ver)
    prepare_build_dir()
    pypi_base = "http://pypi.python.org/packages/source"
    pypi_file = "%s-%s.%s" % (pkg_name,pkg_ver,pkg_type)
    pypi_url  = "%s/%s/%s/%s" % (pypi_base,pkg_name[0],pkg_name,pypi_file)
    pypi_dir  = "%s-%s" % (pkg_name,pkg_ver)
    if os.path.exists(pypi_file):
        print "[skipping download of source package: `%s' already exists]" % pypi_file
    else:
        print "[downloading package source from `%s']" % pypi_url
        urllib.urlretrieve(pypi_url,pypi_file)
    if os.path.isdir(pypi_dir):
        print "[removing existing source dir: `%s']" % pypi_dir
        shutil.rmtree(pypi_dir)
    print "[extracting source from `%s']" % pypi_file
    if pkg_type.count("tar") > 0:
        tarfile.open(pypi_file).extractall()
    elif pkg_type.count("zip") > 0:
        zipfile.ZipFile(pypi_file,"r").extractall()
    patch_python_setup_file(pjoin(pypi_dir,"setup.py"))
    print "[building + installing: `%s']" % pkg_name
    cmd = "cd %s; %s setup.py install" % (pypi_dir,python_bin())
    if not dest_dir is None:
        cmd += " --prefix %s" % dest_dir
    sexe(cmd)

def setup_all():
    """ Builds and installs all packages, as necessary."""
    dest = None
    if len(args) > 0:
        dest = os.path.abspath(Argv()[0])
        prepare_module_dest_dir(dest)
        print "[installing modules to: %s]" % dest
    # distribute is strange, it masquerades as setuptools so
    # we need a special detection method.
    if not check_for_distribute_module("0.6"):
        setup_pypi_package("distribute","0.6.24",force=True,dest_dir=dest)
    else:
        print "[skipping build: 'distribute' is already installed]"
    setup_numpy(dest);
    setup_pypi_package("py","1.4.5","zip",dest_dir=dest)
    setup_pypi_package("pytest","2.1.3","zip",dest_dir=dest)
    setup_pypi_package("pytools","2011.4",dest_dir=dest)
    setup_pypi_package("decorator","3.3.2",dest_dir=dest)
    #setup_pypi_package("pyopencl","2011.1.2",dest_dir=dest)
    setup_pypi_package("ply","3.4",dest_dir=dest)
    setup_pyopencl(dest);

if using_visit:
    if __visit_script_file__ == __visit_source_file__:
        try:
            setup_all()
        except:
            pass
        sys.exit(0)
else:
    if __name__ == "__main__":
        setup_all()
