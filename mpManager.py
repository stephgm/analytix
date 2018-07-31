#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 27 20:34:04 2018

@author: hollidayh
"""

import time
import multiprocessing as mp
import logging
mp.log_to_stderr(logging.DEBUG)

def moduleRun():
    pass

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
    pool = mp.Pool(2)
    for val in [10,8,2,2,2,4]:
        s = str(val)
#        if val > 2:
#            pool.apply_async(worker,args=(val,s),kwargs={'other':'long time'})
#        else:
        pool.apply_async(worker,args=(val,s))
    pool.close()
    pool.join()