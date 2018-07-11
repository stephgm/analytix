#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Thu May 31 20:20:21 2018

@author: hollidayh
"""
import time
import sys
import numpy
import numba

@numba.njit("f8[:](f8[:],f8[:])")
def addThenMultiply(a,b):
    c = numpy.empty(a.size)
    for i in xrange(a.size):
        c[i] = a[i] + b[i]
        c[i] *= 2
    return c

def addThenMultiplyNP(a,b):
    c = a + b
    c *= 2
    return c

n = 1000000
N = 1000
x = numpy.arange(n,dtype='f8')
y = numpy.arange(n,dtype='f8')+4.
#print(x)
#print(y)
tic = time.time()
for i in xrange(N):
    z = addThenMultiply(x,y)
print('numba : '+str(time.time()-tic))
tic = time.time()
for i in xrange(N):
    z = addThenMultiplyNP(x,y)
print('numpy : '+str(time.time()-tic))
sys.exit(0)



#@numba.vectorize(['float64(float64, float64)'], target='cpu')
#@numba.vectorize(['float64(float64, float64)'], target='cuda')
@numba.njit(cache=True)
def Add(a, b):
  return a + b

# Initialize arrays
N = 100000
A = numpy.ones(N, dtype=numpy.float64)
B = numpy.ones(A.shape, dtype=A.dtype)+100
C = numpy.empty(N, dtype=A.dtype)

# Add arrays on GPU
C = Add(A, B)
print(C)
