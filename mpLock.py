#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 14 20:36:44 2018

@author: hollidayh
"""

from multiprocessing import Pool
from collections import OrderedDict

ni = 10000

def worker(iLabel,iVal):
    for i in xrange(10000):
        val = iVal * 100.
    return (iLabel,val)

def callFunction():
    data = OrderedDict()
    for fld in xrange(ni):
        data[str(fld)] = -1
    def append(itup):
        data[itup[0]] = itup[1]
    p = Pool(20)
    for fld in xrange(ni):
        p.apply_async(worker,args=(str(fld),fld),callback=append)
    p.close()
    p.join()
    print(data)

if __name__ == '__main__':
    callFunction()
    