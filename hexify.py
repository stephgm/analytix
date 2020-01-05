#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 30 09:30:28 2019

@author: DivollHJ
"""
import sys
if __name__ == '__main__':
    if len(sys.argv) == 1:
        print('usage : hexify -u <unhex files/dirs> -h <hex files/dirs>')
        print('may use both -u and -h in same command')
        sys.exit(0)
import os
from binascii import hexlify, unhexlify

exthex = hexlify(b'EXTENSION')

def hexify(fname):
    print(fname)
    with open(fname,'rb') as fid:
        binry = hexlify(fid.read())
    fn,ext = os.path.splitext(fname)
    with open(f'{fn}_{ext[1:]}.txt','wb') as fid:
        fid.write(binry)
        fid.write(exthex)
        fid.write(hexlify(ext.encode()))
        
def unhexify(fname):
    with open(fname,'rb') as fid:
        ascry = unhexlify(fid.read()).decode()
    extpos = ascry.rfind('EXTENSION')
    ext = ascry[extpos+9:]
    with open('{}{}'.format(os.path.splitext(fname)[0].rsplit('_',1)[0],ext),'wb') as fid:
        fid.write(ascry[:extpos].encode())
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
            fn,ext = os.path.splitext(thefile)
            if newsubdir:
                if not os.path.isdir(os.path.join(newdir,newsubdir)):
                    os.makedirs(os.path.join(newdir,newsubdir))
                os.rename('{}_{}.txt'.format(fn,ext[1:]),os.path.join(newdir,newsubdir,'{}_{}.txt'.format(os.path.splitext(os.path.basename(thefile))[0],ext[1:])))
            else:
                os.rename('{}_{}.txt'.format(fn,ext[1:]),os.path.join(newdir,'{}_{}.txt'.format(os.path.splitext(os.path.basename(thefile))[0],ext[1:])))
    
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
                os.rename('{}{}'.format(os.path.splitext(thefile)[0].rsplit('_',1)[0],ext),os.path.join(newdir,newsubdir,'{}{}'.format(os.path.splitext(os.path.basename(thefile))[0].rsplit('_',1)[0],ext)))
            else:
                os.rename('{}{}'.format(os.path.splitext(thefile)[0].rsplit('_',1)[0],ext),os.path.join(newdir,'{}{}'.format(os.path.splitext(os.path.basename(thefile))[0].rsplit('_',1)[0],ext)))

if __name__ == '__main__':
    DUN = False
    NUN = False
    filez = {'DUN':[],'NUN':[]}
    dirz  = {'DUN':[],'NUN':[]}
    for arg in sys.argv[1:]:
        print(arg)
        if arg.startswith('-'):
            if arg == '-h':
                DUN = False
                NUN = True
            elif arg == '-u':
                DUN = True
                NUN = False
            else:
                print('Unknown ARG : '+arg)
                sys.exit(1)
            continue
        cp = os.path.realpath(arg)
        if DUN:
            if os.path.isdir(cp):
                dirz['DUN'].append(cp)
            elif os.path.isfile(cp):
                filez['DUN'].append(cp)
        elif NUN:
            if os.path.isdir(cp):
                dirz['NUN'].append(cp)
            elif os.path.isfile(cp):
                filez['NUN'].append(cp)
    for xfile in filez['DUN']:
        unhexify(xfile)
    for xfile in dirz['DUN']:
        unhexifyall(xfile)
    for xfile in filez['NUN']:
        hexify(xfile)
    for xfile in dirz['NUN']:
        hexifyall(xfile)
        
    