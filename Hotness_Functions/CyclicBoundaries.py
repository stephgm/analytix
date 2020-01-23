#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 22 18:39:17 2020

@author: Jordan
"""

import numpy as np
from six import string_types


def isIterable(iItem,**kwargs):
    '''
    Checks if the iItem is an iterable. Can toggle whether or not you consider
    a string iterable.
    Input:
            iItem - python Object
    Kwargs:
            strOk - False = Return False if iItem is a string
                    True = Return True if iItem is a string
    Return:
            Returns True if iItem is an iterable, else return False
    '''
    acceptstrings = kwargs.get('strOk',False)
    if not acceptstrings:
        if isinstance(iItem,string_types):
            return False
        try:
            iter(iItem)
            return True
        except:
            return False
    else:
        try:
            iter(iItem)
            return True
        except:
            return False


def cyclicBoundary(lowlimit,highlimit,value,**kwargs):
    '''
    Function that takes care of values that should only exist between a specific range.
    A good example of this are angles. 
    The standard set of angles exists over the range [0-360]
    Given a value of 363, would yield a result of 3.  Because in the world of
    angles, 363 == 3 and in fact 0 == 360. Likewise, -1 == 359, -270 == 90, etc. 
    This is known as a cyclic boundary; it wraps back around on itself within the range.
    
    Inputs:
        lowlimit - a number that represents the lower boundary
        highlimit - a number that represents the upper boundary
        value - a number or iterable that needs to be normalized to the range of values
                determined by the lowlimit and highlimit
    
    Kwargs:
        N/A
    
    Return:
        Returns the corrected value or values that are now defined within the range
    '''
    if isinstance(value,(int,float)):
        if lowlimit <= value and highlimit > value:
            return value
        else:
            r = highlimit - lowlimit
            value = value%r
            if value > highlimit:
                value -= r
            elif value < lowlimit:
                value += r
        return value
    elif isIterable(value):
        if isinstance(value,np.ndarray):
            dtype = np.array
        else:
            dtype = type(value)
        value = np.array(value)
        idx = (lowlimit < value) & (highlimit > value)
        if idx.all():
            return dtype(value)
        else:
            r = highlimit - lowlimit
            value = value%r
            hidx = value > highlimit
            lidx = value < lowlimit
            if hidx.any():
                value[hidx] -= r
            if lidx.any():
                value[lidx] += r
            return dtype(value)
    else:
        return value
