#!/usr/bin/python
import sys
import os
#from struct import Struct
import ctypes
import numpy
import time
ecr = numpy.arange(3.)
eci = numpy.empty(3)
print(ecr)
print(eci)
so = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'libfoo.so')
print(so)
tic = time.time()
lib = ctypes.CDLL(so)
lib.ecr2eci(eci.ctypes,ecr.ctypes)
po = numpy.empty((18,18))
p = numpy.empty(18)
lib.editPoly(p.ctypes,po.ctypes)
print(p)
print(po)
#import foo
#foo.ecr2eci(eci.ctypes,ecr.ctypes)
#print(time.time()-tic)
#print(ecr)
#print(eci)
sys.exit()
so = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'file.so')
lib = ctypes.CDLL(so)
arr = numpy.random.random((20,2))
arr[:,0] = numpy.arange(20.)

arr = numpy.arange(10.)
print(arr)
lib.function(arr.ctypes,len(arr))
print(arr)
sys.exit()

#up = Struct('<d').unpack
#with open("data.bin",'r') as fid:
#    arr = numpy.fromstring(fid.read(),'<f8')
#arr = numpy.fromfile('data.bin','<f8')
#print(arr)
#sys.exit(0)
"""
import sys
import os
import time
import ctypes
import foo
import math
LIB_PATH = os.path.dirname(os.path.realpath(__file__))
cfoo = ctypes.cdll.LoadLibrary(os.path.join(LIB_PATH,'libfoo.so'))
nloops = 10000
def vincenty(iLat,iLon):
    i = 0
    tmp = 0.0
    while i < 1000:
	i+=1
        tmp = math.sin(iLat)**iLon
    return tmp

j = ctypes.c_double(14.)
k = ctypes.c_double(15.)
i = 0
tmp = [0.0] * nloops
tic = time.time()
for i in xrange(nloops):
    tmp[i] = foo.vincenty(14.,15.)
t1 = time.time() - tic
print(tmp[:3])
tmp = [ctypes.c_double(0.0)] * nloops
#tmp = [0.0] * nloops
for i in xrange(nloops):
    tmp[i] = vincenty(14.,15.)
t2 = time.time() - tic
print(tmp[:3])
print(t1)
print(t2)
sys.exit(0)
"""
"""
from ctypes import *

fh = CDLL("./libfoo.so")

s = fh.foo()

i = fh.get3(3)

print(i)
print(i+1)
"""
"""
import foo
ecr = [-1.] * 3
eci = [1.,88.45,32.7765];

foo.ecr2eci(ecr,eci)

print(ecr)
print(eci)
"""

"""
import ctypes

foo = ctypes.cdll.LoadLibrary(os.path.join(LIB_PATH,'libfoo.so'))

this = (ctypes.c_double * 3)(0.,0.,0.)
that = (ctypes.c_double * 3)(88.8,-1.0, 45.0)
for i in xrange(len(this)):
    print(this[i])
    print(that[i])
foo.ecr2eci(this,that)
print('****')
for i in xrange(len(this)):
    print(this[i])
    print(that[i])
nv = (ctypes.c_double * 4)(0.0,0.0,0.0,0.0)
foo.propVector(nv)
for j in nv:
    print(j);
#print(that)
"""
import sys
import foo
foo.foo()
foo.passFunction2()
foo.setGlobals()
foo.passFunction2()
#val = foo.add(4.0,5.0)
#print(val)
#data = foo.propVector2(1.,2.,3.,4.,5.,6.)
#print(data)
#foo.passFunction()
#i = foo.vincenty(14.,1.)
sys.exit(0)
"""
import ctypes
foo = ctypes.cdll.LoadLibrary(os.path.join(LIB_PATH,'libfoo.so'))
vect1 = (ctypes.c_double * 10)()
vect2 = (ctypes.c_double * 10)()
foo.ecr2eci(vect1,vect2)
for val in vect1:
    print(val)
#for val in vect:
#    print(val)
foo.foo()
vect1[0] = 1.0;
vect1[1] = 2.0;
vect1[2] = 3.0;
vect1[3] = 4.0;
vect1[4] = 5.0;
vect1[5] = 6.6;
vect1 = (ctypes.c_double * 6)(1.0,2.0,3.0,4.0,5.0,6.6)
foo.callPropVector(vect1)
print('Finished')
"""
