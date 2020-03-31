#!/usr/bin/env py3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 20 11:58:13 2019

@author: HollidayHP
"""
import sys
import os
import numpy as np

RELATIVE_LIB_PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __name__ == '__main__':
    sys.path.append(RELATIVE_LIB_PATH)
    sys.path.pop(0)

iSize = [(-128,127,np.int8),
         (-32768,32767,np.int16),
         (-2147483648,2147483647,np.int32),
         (-9223372036854775808,9223372036854775807,np.int64)]

uSize =[(255,np.uint8),
        (65535,np.uint16),
        (4294967295,np.uint32),
        (18446744073709551615,np.uint64)]

def downsizeInt(ia):
     if ia.dtype.kind == 'u':
         for n,t in uSize:
               idx = (ia <= n)
               if idx.all():
                  return t
     elif ia.dtype.kind == 'i':
           for nl,nh,t in iSize:
                idx = (ia>=nl) & (ia <=nh)
                if idx.all():
                    return t
     else:
         return ia.dtype

def multiDims(arr,newlist):
    if isinstance(arr,np.ndarray):
        if arr.ndim > 2:
            for nextarr in arr:
                newlist.append([])
                multiDims(nextarr,newlist[-1])
        elif arr.ndim == 2:
            for nextarr in arr:
                if nextarr.dtype.kind in ('U','O','S'):
                    newlist.append(list(map(bytes,nextarr)))
                else:
                    newlist.append(list(nextarr))
        else:
            if arr.dtype.kind in ('U','O','S'):
                newlist = list(map(bytes,arr))
            else:
                newlist = list(arr)
        return newlist
    elif isinstance(arr,list):
        return [multiDims(nextarr,[]) for nextarr in arr]
    elif isinstance(arr,tuple):
        return tuple([multiDims(nextarr,[]) for nextarr in arr])
    else:
        return arr
