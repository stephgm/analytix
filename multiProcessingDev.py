# -*- coding: utf-8 -*-
"""
Created on Tue Feb 18 20:54:24 2020

@author: HollidayHP
"""
import sys
import os
import signal
import time
from multiprocessing import Pool
from subprocess import Popen, PIPE

def foo(i):
    # print(f'HERE : {i}')
    p = Popen(['timeout','2'],stdout=PIPE, stderr=PIPE)
    try:
        p.communicate(timeout=1)
    except:
        print(f'FAIL : {i}')
        os.kill(p.pid,signal.SIGINT)
        return
    p.wait()
    print(f'FINISHED : {i}')

if __name__ == '__main__':
    pool = Pool(3)
    # with Pool(3) as pool:
    for i in range(9):
        pool.apply_async(foo,args=(i,))
    pool.close()
    pool.join()