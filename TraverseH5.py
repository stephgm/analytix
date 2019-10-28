#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 28 13:33:39 2019

@author: klinetry
"""
import h5py


def traverseH5(srcgrp,dsDict,**kwargs):
    # Required for -truth.h5 files to make sure full set of columns will be used
    forcecommon = kwargs.get('forcecommon',False)
    # If it is a group
    if isinstance(srcgrp,h5py._hl.group.Group):
        # Check if there is a group within the gorup, need to do this so we keep looping the objects
        # in the group after a traversH5 recursion call
        grpChk = [True for x in map(srcgrp.get,srcgrp.keys()) if isinstance(x,h5py._hl.group.Group)]
        stopLevel = False
        for k in srcgrp:
            # Keep recursing if it's a group or a hard link
            if (isinstance(srcgrp.get(k,getlink=True),h5py._hl.group.HardLink) or
                isinstance(srcgrp[k],h5py._hl.group.Group)): # and not srcgrp[k].name.startswith('/dbo.'):
                stopLevel = traverseH5(srcgrp[k],dsDict,forcecommon=forcecommon)
            # return will be true if it traversed down to a dataset, false if a group (so keep looping)
            if stopLevel and not grpChk:
                break
        return False
    # Not a group, so it must be a dataset
    else:
        # A structured array type dataset (think topic_log_All.h5)
        if isinstance(srcgrp.dtype.names,tuple):
            # if we havent already added it
            if srcgrp.parent.name not in dsDict:
                # Get the column names of the first dataset
                curCols = set(srcgrp.dtype.names)
                curGrp = os.path.basename(srcgrp.name)
                colDiff = set()
                # Loop through the other objects in the parent group, this is a test for common columns
                for k in srcgrp.parent:
                    # If its not a group and no the one we started with
                    if not isinstance(srcgrp.parent[k],h5py._hl.group.Group) and k != curGrp:
                        # If its not a structured array, then it is automatically not common columns
                        if not isinstance(srcgrp.parent[k].dtype.names,tuple):
                            colDiff = ['Mixed']
                        else:
                            # If the two sets of dtype names are different, it's not common columns
                            colDiff = curCols.symmetric_difference(set(srcgrp.parent[k].dtype.names))
                        # Breaking on the first one for speed, this may mean we say common columns when it's not actually
                        break
                # If the set of differences is greater than 0 we have different column names
                if len(colDiff) > 0 and srcgrp.parent.name not in dsDict:
                    dsDict[srcgrp.parent.name] = {}
                    dsDict[srcgrp.parent.name]['type'] = 'STRUCT'
                    dsDict[srcgrp.parent.name]['commoncol'] = False

                    # Go through each item that is not a group and is a structured array
                    # set an entry in the dictionary using the dataset name and listing the column headers
                    # if there are "LIST" type datasets at this level as well, they will be skipped (.truthMap.pkl)

                    for k in srcgrp.parent:
                        if not isinstance(srcgrp.parent[k],h5py._hl.group.Group) and \
                                isinstance(srcgrp.parent[k].dtype.names,tuple):
                            dsDict[srcgrp.parent.name][k] = list(srcgrp.parent[k].dtype.names)
                #These are structured arrays with all the same column headers, cols is the headers,
                # objs is all the names of the datasets at that Level

                else:
                    dsDict[srcgrp.parent.name] = {}
                    dsDict[srcgrp.parent.name]['type'] = 'STRUCT'
                    dsDict[srcgrp.parent.name]['commoncol'] = True
                    dsDict[srcgrp.parent.name]['cols'] = list(srcgrp.dtype.names)
                    dsDict[srcgrp.parent.name]['objs'] = [k for k in srcgrp.parent.keys()
                                                            if isinstance(srcgrp.parent[k],h5py._hl.dataset.Dataset)]

            # A group full of datasets each representing a column (think .AllElement.h5)
            else:
                if srcgrp.parent.parent.name not in dsDict:
                    # -truth.h5, make 'em common even if the first two wouldn't be, cols are the headers, objs are the datasets

                    if forcecommon:
                        dsDict[srcgrp.parent.parent.name] = {}
                        dsDict[srcgrp.parent.parent.name]['type'] = 'LIST'
                        dsDict[srcgrp.parent.parent.name]['commoncol'] = True
                        dsDict[srcgrp.parent.parent.name]['cols'] = list(srcgrp.parent.keys())
                        dsDict[srcgrp.parent.parent.name]['objs'] = list(srcgrp.parent.parent.keys())
                    else:
                        # For this structure, the keys of the parent are the column names, so now loop through the other
                        # groups at the parent level and get the keys for those, common col if they are the same
                        curCols = set(srcgrp.parent.keys())
                        curGrp = os.path.basename(srcgrp.parent.name)
                        colDiff = set()
                        for k in srcgrp.parent.parent:
                            if isinstance(srcgrp.parent.parent[k],h5py._hl.group.Group) and k != curGrp:
                                colDiff = curCols.symmetric_difference(set(srcgrp.parent.parent[k].keys()))
                                if len(colDiff) > 0:
                                    break
                        # If there's a difference they are not common, keys at the 'datasets' which are the parent group names
                        # those keys point to the column names which are the keys of the groups

                        if len(colDiff) > 0:
                            dsDict[srcgrp.parent.parent.name] = {}
                            dsDict[srcgrp.parent.parent.name]['type'] = 'LIST'
                            dsDict[srcgrp.parent.parent.name]['commoncol'] = False
                            for k in srcgrp.parent.parent:
                                if isinstance(srcgrp.parent.parent[k],h5py._hl.group.Group):
                                    dsDict[srcgrp.parent.parent.name][k] = list(srcgrp.parent.parent[k].keys())
                        # They are common, so cols is the column headers, objs are the parent group names 'datasets'
                        else:
                            dsDict[srcgrp.parent.parent.name] = {}
                            dsDict[srcgrp.parent.parent.name]['type'] = 'LIST'
                            dsDict[srcgrp.parent.parent.name]['commoncol'] = True
                            dsDict[srcgrp.parent.parent.name]['cols'] = list(srcgrp.parent.keys())
                            dsDict[srcgrp.parent.parent.name]['objs'] = list(srcgrp.parent.parent.keys())
                    # List comprehension of all cols get dtype
    return True # Once you've gone thorugh all the items at this level return (unrecurse?)
