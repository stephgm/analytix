#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 15 17:55:26 2019

@author: hollidayh
"""
import os
import resource
import numpy
from multiprocessing import Pool
import time

MEM_TO_GB = 1024.

def get_total_memory():
    with open('/proc/meminfo', 'r') as mem:
        for i in mem:
            return float(i.split()[1]) / 1024. / 1024.

def get_memory():
    with open('/proc/meminfo', 'r') as mem:
        free_memory = 0
        for i in mem:
            sline = i.split()
            if str(sline[0]) in ('MemFree:', 'Buffers:', 'Cached:'):
                free_memory += int(sline[1])
    return free_memory / 1024. / 1024.

def get_memory_bytes():
    with open('/proc/meminfo', 'r') as mem:
        for i in mem:
            sline = i.split()
            if str(sline[0]) == 'MemAvailable:':
                # this is in KB, convert to bytes
                return int(sline[1]) * 1024
def memory_limit():
    percentage = 0.1
    # percentage = 0.5
    soft, hard = resource.getrlimit(resource.RLIMIT_AS)
    resource.setrlimit(resource.RLIMIT_AS, (get_memory_bytes() * percentage, hard))

def reset_limits():
    resource.setrlimit(resource.RLIMIT_AS, (-1, -1))

def worker(timeout):
    try:
        a = numpy.empty(10000000)
        # murdered the laptop, but 50% saved it
        #a = numpy.empty(100000000)
        b = [a.copy()]
        b.append(a.copy())
        print('{} sleeping'.format(timeout))
        time.sleep(timeout)
    except MemoryError:
        print('Memory Error Handled')
        return
    print('{} exiting'.format(timeout))

def start_threads():
    pool = Pool(2)
    pool.apply_async(worker,args=(10,))
    pool.apply_async(worker,args=(8,))
    pool.close()
    pool.join()

if __name__ == '__main__':
    tot = get_total_memory()
#    print(tot)
    memory_limit()
    reset_limits()
    start_threads()
    # now used memory
#    print(tot - get_memory())
#    print(tot - get_memory2())
    #os.system('free -b')