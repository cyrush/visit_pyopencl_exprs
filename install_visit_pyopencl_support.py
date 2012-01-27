# [VisIt Python Script]
#
# ${disclaimer}
#
"""
 file: install_visit_pyopencl_support.py
 author: Cyrus Harrison <cyrush@llnl.gov>
 description:
  Installs pyopencl and all supporting modules (including numpy) into
  a VisIt install.

 usage:
 >visit -nowin -cli -s install_visit_pyopencl_support.py <destination-dir>
"""

import os
import sys
import subprocess
import shutil
import urllib
import tarfile
import zipfile

from os.path import join as pjoin

def sexe(cmd,echo=True):
    """ Shell command helper. """
    print "[exe: %s]"% cmd
    subprocess.call(cmd,shell=True)

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
    print "[cloning `numpy' github repo (https://github.com/numpy/numpy.git)]"
    sexe('git clone https://github.com/numpy/numpy.git')
    patch_python_setup_file(pjoin("numpy","setup.py"),seed="import subprocess\n")
    print "[building + installing: `numpy']"
    cmd ="cd numpy; visit -nowin -cli -s setup.py install"
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
    cmd = "cd %s; visit -nowin -cli -s setup.py install" % pypi_dir 
    if not dest_dir is None:
        cmd += " --prefix %s" % dest_dir
    sexe(cmd)

def setup_all():
    """ Builds and installs all packages, as necessary."""
    dest = None
    if len(Argv()) > 0:
        dest = os.path.abspath(Argv()[0])
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
    setup_pypi_package("pyopencl","2011.1.2",dest_dir=dest)

if __visit_script_file__ == __visit_source_file__:
    try:
        setup_all()
    except:
        pass
    sys.exit(0)