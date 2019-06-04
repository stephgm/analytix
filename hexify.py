# -*- coding: utf-8 -*-
"""
Created on Thu May 30 09:30:28 2019

@author: DivollHJ
"""
import os
from binascii import hexlify, unhexlify

exthex = hexlify('EXTENSION')

def hexify(fname):
    with open(fname,'r') as fid:
        binry = hexlify(fid.read())
    fn,ext = os.path.splitext(fname)
    with open('{}.txt'.format(fn),'w') as fid:
        fid.write('{}{}{}'.format(binry,exthex,hexlify(ext)))
        
def unhexify(fname):
    with open(fname,'r') as fid:
        ascry = unhexlify(fid.read())
    extpos = ascry.rfind('EXTENSION')
    ext = ascry[extpos+9:]
    with open('{}{}'.format(os.path.splitext(fname)[0],ext),'w') as fid:
        fid.write(ascry[:extpos])
    return ext

def hexifyall(dname):
    if os.path.isdir(dname):
        superdir = os.path.dirname(dname)
        bname = os.path.basename(dname)
        newdir = os.path.join(superdir,'{}_hexified'.format(bname))
        if not os.path.isdir(newdir):
            os.makedirs(newdir)
        thefiles = [os.path.join(root,xfile) for root, dirs, files in os.walk(dname)
                        for xfile in files]
        for thefile in thefiles:
            hexify(thefile)
            newsubdir = thefile[len(dname)+1:-(len(os.path.basename(thefile))+1)]
            if newsubdir:
                if not os.path.isdir(os.path.join(newdir,newsubdir)):
                    os.makedirs(os.path.join(newdir,newsubdir))
                os.rename('{}.txt'.format(os.path.splitext(thefile)[0]),os.path.join(newdir,newsubdir,'{}.txt'.format(os.path.splitext(os.path.basename(thefile))[0])))
            else:
                os.rename('{}.txt'.format(os.path.splitext(thefile)[0]),os.path.join(newdir,'{}.txt'.format(os.path.splitext(os.path.basename(thefile))[0])))
    
def unhexifyall(dname):
    if os.path.isdir(dname):
        superdir = os.path.dirname(dname)
        bname = os.path.basename(dname)
        newdir = os.path.join(superdir,bname[:-len('_hexified')])
        if not os.path.isdir(newdir):
            os.makedirs(newdir)
        thefiles = [os.path.join(root,xfile) for root, dirs, files in os.walk(dname)
                        for xfile in files]
        for thefile in thefiles:
            ext = unhexify(thefile)
            newsubdir = thefile[len(dname)+1:-(len(os.path.basename(thefile))+1)]
            if newsubdir:
                if not os.path.isdir(os.path.join(newdir,newsubdir)):
                    os.makedirs(os.path.join(newdir,newsubdir))
                os.rename('{}{}'.format(os.path.splitext(thefile)[0],ext),os.path.join(newdir,newsubdir,'{}{}'.format(os.path.splitext(os.path.basename(thefile))[0],ext)))
            else:
                os.rename('{}{}'.format(os.path.splitext(thefile)[0],ext),os.path.join(newdir,'{}{}'.format(os.path.splitext(os.path.basename(thefile))[0],ext)))
    