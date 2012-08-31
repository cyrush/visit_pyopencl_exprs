
def elapsed(event):
    return 1e-9*(event.profile.end - event.profile.start)

def tinfo(nm,size,**kwargs):
    csv = "|csv,%s, %d" % (nm,size)
    js = "{'dv':'%s','sz': %d"% (nm,size)
    for k,v in kwargs.items():
        js  += ", '%s':%s" % (k,repr(v))
        csv += ', %s' % repr(v)
    js +="}"
    print js
    print csv
    return js,csv

def mb_2_nfloat32(mb):
    return 1024*1024//4 * mb