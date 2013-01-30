
def elapsed(val):
    if isinstance(val,(int, long, float)):
        return 1e-9*(val)
    else:
        return 1e-9*(val.profile.end - val.profile.start)

def tinfo(nm,size,**kwargs):
    csv = "|csv,%s, %d" % (nm,size)
    js = "{'dv':'%s','sz': %d"% (nm,size)
    for k,v in kwargs.items():
        if isinstance(v,(int, long, float)):
            tv = repr(v)
        else:
            tv = repr(elapsed(v))
        js  += ", '%s':%s" % (k,tv)
        csv += ', %s' % tv
    js +="}"
    print js
    print csv
    return js,csv

def mb_2_nfloat32(mb):
    return 1024*1024//4 * mb