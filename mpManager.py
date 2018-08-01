#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 27 20:34:04 2018

@author: hollidayh
"""

import sys
import os
import time
import multiprocessing as mp
#import logging
#mp.log_to_stderr(logging.DEBUG)
from subprocess import Popen

def moduleRun(iFolder,iPyFile,iFunction,*args,**kwargs):
    line = ['import sys']
    line.append('import os')
    mloc = os.path.join(os.path.dirname(os.path.realpath(__file__)),iFolder)
    #line.append('sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)),"'+iFolder+'"))')
    line.append('sys.path.append("'+mloc+'")')
    line.append('from '+iPyFile+' import '+iFunction)
    line.append('try:')
    callstr = '    '+iFunction[:]+'('
    for i,arg in enumerate(args):
        if i:
            callstr += ','
        if isinstance(arg,basestring):
            callstr += '"'+arg+'"'
        else:
            callstr += str(arg)
    if kwargs:
        callstr += ','
    for i,fld in enumerate(kwargs.keys()):
        if i:
            callstr += ','
        if isinstance(kwargs[fld],basestring):
            callstr += '"'+kwargs[fld]+'"'
        else:
            callstr += ''+fld+'='+str(kwargs[fld])
    callstr += ')'
    line.append(callstr)
    line.append('except:')
    line.append('    import traceback')
    line.append('    traceback.print_exc()')
    #print('\n'.join(line))
    Popen([sys.executable,'-c','\n'.join(line)]).wait()
    

def worker(i,iStr,**kwargs):
    other = kwargs.pop('other','')
    thisName = mp.current_process().name+' ('+iStr+')'
    print('Starting '+thisName)
    time.sleep(i)
    print('Finished '+thisName)
    
def manage(x,nt):
    nactive = 0
    finished = [False] * len(x)
    started  = [False] * len(x)
    while True:
        if all(finished):
            break
        cna = 0
        for i,p in x:
            if p.is_alive():
                started[i] = True
                cna += 1
                if cna == nt:
                    break
            p.start()
        time.sleep(1)
if __name__ == '__main__':
    moduleRun('modules','utils','thisAnalysis','/storage/events')
    moduleRun('modules','utils','thisAnalysis','/storage/events',this=True,force=False)
#    pool = mp.Pool(2)
#    for val in [10,8,2,2,2,4]:
#        s = str(val)
#        pool.apply_async(worker,args=(val,s))
#    pool.close()
#    pool.join()