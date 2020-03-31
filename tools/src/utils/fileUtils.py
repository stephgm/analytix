#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 29 16:29:52 2020

@author: hollidayh
"""
import sys
import os
from struct import unpack
import h5py
import json
import pandas as pd
import numpy as np

RELATIVE_LIB_PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __name__ == '__main__':
    sys.path.append(RELATIVE_LIB_PATH)
    sys.path.pop(0)

from misc_functions.numpy_utils import downsizeInt

h5pyStr = h5py.special_dtype(vlen=str)
sizeDiv = {'S':1,'U':4}

def checkOType(series, **kwargs):
    if not isinstance(series,(pd.Series,pd.DataFrame,np.ndarray)):
        return False
    if series.dtype.kind in ('S','U'):
        return np.array(series,dtype=f'{series.dtype.kind}{int(series.dtype.itemsize/sizeDiv[series.dtype.kind])}')
    elif series.dtype.kind == 'O':
        # so len field on float does not fail
        series.fillna('',inplace=True)
        series = series.astype(np.str)
        # return np.array(series.apply(bruteForceString),dtype=f'S{len(max(series.values,key=len))}')
        return np.array(series,dtype=f'S{len(max(series.values,key=len))}')
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
    if isinstance(ia,bytes):
        return ia.decode('utf-8','ignore')
    else:
        return ia

def traverseH5(srcgrp, dsDict, **kwargs):
    # Required for -truth.h5 files to make sure full set of columns will be
    # used.
    forcecommon = kwargs.get('forcecommon', False)

    # If it's a group...
    if isinstance(srcgrp, h5py._hl.group.Group):
        # Check if there's a group within the group.  Need to do this so
        # we keep looping the objects in the group after a traverseH5
        # recursion call.
        grpChk = [ True for x in map(srcgrp.get, srcgrp.keys()) if isinstance(x, h5py._hl.group.Group)]
        stopLevel = False
        for k in srcgrp:
            # Keep recursing if it's a group or a hard link.
            if (isinstance(srcgrp.get(k, getlink=True), h5py._hl.group.HardLink) or \
                isinstance(srcgrp[k], h5py._hl.group.Group)): # and not srcgrp[k].name.startswith('/dbo.'):
                stopLevel = traverseH5(srcgrp[k], dsDict, forcecommon=forcecommon)

            # Retrun will be true if it traversed down to a dataset, false if a group (so keep looping)
            if stopLevel and not grpChk:
                break
        return False
    else:
        # Must be a dataset.

        # A structured array type dataset (think topic_log_All.h5)
        if isinstance(srcgrp.dtype.names, tuple):
            # If we haven't already added it
            if srcgrp.parent.name not in dsDict:
                # Get the column names of the first dataset
                curCols = set(srcgrp.dtype.names)
                curGrp = os.path.basename(srcgrp.name)
                colDiff = set()

                # Loop through the other objects in the parent group, this is a test for common columns.
                for k in srcgrp.parent:
                    # If it's not a group and not the one we started with
                    if not isinstance(srcgrp.parent[k], h5py._hl.group.Group) and k != curGrp:
                        # if it's not a structured array then it's automatically not common columns
                        if not isinstance(srcgrp.parent[k].dtype.names, tuple):
                            colDiff = ['Mixed']
                        else:
                            # if the two sets of dtype names are different it's not common columns.
                            colDiff = curCols.symmetric_difference(set(srcgrp.parent[k].dtype.names))
                        # Breaking on the first one for speed.  This may mean we say common columns when it's not actually
                        #break
                # If the set of differences is greater than 0 we have different column names.
                if len(colDiff) > 0 and srcgrp.parent.name not in dsDict:
                    dsDict[srcgrp.parent.name] = {}
                    dsDict[srcgrp.parent.name]['type'] = 'STRUCT'
                    dsDict[srcgrp.parent.name]['commoncol'] = False
                    # Go through each items that is not a group and is a structured array.
                    # set an entry in the dictionary using the dataset name and listing the column headers
                    # If there are 'LIST' type datasets at this level as well they will be skipped (.trustMap.pkl)
                    for k in srcgrp.parent:
                        if not isinstance(srcgrp.parent[k], h5py._hl.group.Group) and \
                            isinstance(srcgrp.parent[k].dtype.names, tuple):
                            dsDict[srcgrp.parent.name][k] = list(srcgrp.parent[k].dtype.names)
                # These are structured arrays with all the same column headers.  cols is the headers and objs is all the names of the datasets at that level.
                else:
                    dsDict[srcgrp.parent.name] = {}
                    dsDict[srcgrp.parent.name]['type'] = 'STRUCT'
                    dsDict[srcgrp.parent.name]['commoncol'] = True
                    dsDict[srcgrp.parent.name]['cols'] = list(srcgrp.dtype.names)
                    dsDict[srcgrp.parent.name]['objs'] = [ k for k in srcgrp.parent.keys() if isinstance(srcgrp.parent[k], h5py._hl.dataset.Dataset) ]
        # A group full of datasets each representing a column (think .AllElements.h5)
        else:
            if srcgrp.parent.parent.name not in dsDict:
                # -truth.h5 make them common even if the first two wouldn't be.  cols are the headers objs are the datasets
                if forcecommon:
                    dsDict[srcgrp.parent.name] = {}
                    dsDict[srcgrp.parent.name]['type'] = 'STRUCT'
                    dsDict[srcgrp.parent.name]['commoncol'] = True
                    dsDict[srcgrp.parent.name]['cols'] = list(srcgrp.parent.keys())
                    dsDict[srcgrp.parent.name]['objs'] = list(srcgrp.parent.parent.keys())
                else:
                    # For this structure the keys of the parent are the column names, so now loop through the
                    # other groups at the parent level and get the keys for those, common col if they are the same.
                    curCols = set(srcgrp.parent.keys())
                    curGrp = os.path.basename(srcgrp.parent.name)
                    colDiff = set()
                    for k in srcgrp.parent.parent:
                        if isinstance(srcgrp.parent.parent[k], h5py._hl.group.Group) and k != curGrp:
                            colDiff = curCols.symmetric_difference(set(srcgrp.parent.parent[k].keys()))
                            if len(colDiff) > 0:
                                break
                    # If there's a differenced they are not common.  Keys at the datasets which are parent group names
                    # those keys point to the column names which are the keys of the groups.
                    if len(colDiff) > 0:
                        dsDict[srcgrp.parent.parent.name] = {}
                        dsDict[srcgrp.parent.parent.name]['type'] = 'LIST'
                        dsDict[srcgrp.parent.parent.name]['commoncol'] = False
                        for k in srcgrp.parent.parent:
                            if isinstance(srcgrp.parent.parent[k], h5py._hl.group.Group):
                                dsDict[srcgrp.parent.parent.name][k] = list(srcgrp.parent.parent[k].keys())
                    else:
                        # They are common so cols is the column headers, objs are the parent grop names 'datasets'.
                        dsDict[srcgrp.parent.parent.name] = {}
                        dsDict[srcgrp.parent.parent.name]['type'] = 'LIST'
                        dsDict[srcgrp.parent.parent.name]['commoncol'] = True
                        dsDict[srcgrp.parent.parent.name]['cols'] = list(srcgrp.parent.keys())
                        dsDict[srcgrp.parent.parent.name]['objs'] = list(srcgrp.parent.parent.keys())
        # list comprehension of all cols get dtype
    return True # once you've gone through all the items at this level return (unrecurse?)

def genDSDict(iH5file):
    dsDict = {}
    with h5py.File(iH5file,'r') as fid:
        traverseH5(fid,dsDict,forcecommon=False)
    with open(f'{os.path.splitext(iH5file)[0]}.json','w') as fid:
        json.dump(dsDict,fid)