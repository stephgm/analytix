#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 29 16:29:52 2020

@author: hollidayh
"""

# import sys
# import os
from struct import unpack
import h5py
import pandas as pd
import numpy as np

h5pyStr = h5py.special_dtype(vlen=str)

sizeDiv = {'S':1,'U':4}

def downsizeInt():
    return

def checkOType(series, **kwargs):
    if not isinstance(series,(pd.Series,pd.DataFrame,np.ndarray)):
        return False
    if series.dtype.kind in ('S','U'):
        return np.array(series,dtype=f'{series.dtype.kind}{int(series.dtype.itemsize/sizeDiv[series.dtype.kind])}')
    elif series.dtype.kind == 'O':
        # so len field on float does not fail
        series.fillna('',inplace=True)
        series = series.astype(np.str)
        return np.array(series.apply(bruteForceString),dtype=f'S{len(max(series.values,key=len))}')
    elif series.dtype.kind in ('u','i'):
        return np.array(series,dtype=downsizeInt(series))
    else:
        return series


def writeDFtoListH5(grp,arr,**kwargs):
    if arr.shape[0]:
        for dset in arr:
            grp.create_dataset(dset,data=checkOType(arr[dset]))

def unpack_decode(msgFmt,buff):
    return tuple([item.decode('utf-8') \
                  if isinstance(item,bytes) else item for item in unpack(msgFmt,buff)])

def bruteForceString(ia):
    return ia.decode('utf-8','ignore')

