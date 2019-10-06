#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Oct  4 19:07:28 2019

@author: klinetry
"""
'''
Notes:  These function will work for any of the following iterable objects
that we use commonly List, Tuple, Dictionary, DataFrame, and StrucArrays.
Even if the function requires a fieldname, lists and tuples will be handled
to return something that makes sense.  String objects are iterable in Python,
however, unless otherwise stated in the comments below each function declaration
they will be treated as non-iterables.
'''

from collections import Iterable,OrderedDict
from functools import partial
import numpy as np
import pandas as pd
import inspect
import copy

#Set True if you want to debug the functions being used.
debug = True

def CCprint(msg,origin=''):
    '''
    For debugging purposes.  Will print where the function was called from
    along with the debug message found in this file.  Args are self explanitory.
    '''
    print('{} from [{}] -> [{}]'.format(msg,origin,inspect.stack()[1][3]))

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
        return isinstance(iItem,Iterable) and not isinstance(iItem,basestring)
    else:
        return isinstance(iItem,Iterable)

def handleMixedDictTypes(iItem,oItem,**kwargs):
    '''
    Ensures that the output Dict (oItem) has the same types as input Dict (iItem)
    No checks required.  It should be used on 2 dictionaries only. Obviously the
    keys must match from iItem to oItem

    Note: Slower, but safer if you copy.copy:  timeit ~ 3.28 microseconds per loop
    Note: Fastest if you don't care to alter the original.  Which you shouldn't if
    you're using this function.  Clearly you intend to change the type of the
    dictionary oItem anyways: timeit ~ 1.98 microseconds per loop

    For functions in this file, it doesn't matter if we change the original
    because they come from dataframes, which makes a copy anyways.
    '''
    for key in iItem.keys():
        if key in oItem:
            keytype = type(iItem[key])
            if keytype == np.ndarray:
                oItem[key] = np.array(oItem[key],dtype=iItem[key].dtype)
            else:
                oItem[key] = keytype(oItem[key])
    return oItem

def getFailReturn(iItem,**kwargs):
    '''
    Returns the empty value of the datatype of iItem.
    This is needed because numpy arrays are the only things that fail
    if you do
    rtype = type(iItem);  return rtype();  Which is stupid.
    '''
    rtype = type(iItem)
    if rtype == np.ndarray:
        return np.empty(0,dtype=iItem.dtype)
    else:
        return rtype()

def handleValue(iItem,header,value):
    '''
    Returns the correct type of the value to compare with dataframe column type.
    '''
    if header in iItem:
        dtype = iItem[header].dtype.kind
        if dtype in ['u','i']:
            try:
                value = int(value)
            except:
                return None
        elif dtype in ['b']:
            try:
                value = value == 'True'
            except:
                return None
        elif dtype in ['f']:
            try:
                value = float(value)
            except:
                return None
        else:
            value = str(value)
    else:
        return None
    return value


def SortFields(iItem,fieldnames,**kwargs):
    '''
    Sorts Dictionaries, DataFrames, and Structured Arrays on fieldname(s) in
    ascending or descending order. Supports dictionaries with mixed types for
    example: {'this':(0,1),'that':[1,2],'wbb':np.array([2,3])} and returns a
    dictionary with the same types.

    Input:
            iItem - dictionary, stuctured array, or dataframe
            fieldnames - string or list of strings of the fields to sort

    Kwargs:
            gtzero - bool or list of bool to filter greater than zero.
                     Will assume False unless otherwise stated
                     Note:
                             If you send list of fields, and set gtzero = False/True
                         This one value will be applied to all fields in fieldnames
                             If you send a list of fields and a list of gtzero,
                         they must be the same length.
                             If you send one fieldname and a list of gtzero,
                         the first value for gtzero will be used by default.
            ascend - bool or list of bool to sort in ascending order.
                     Will assume True unless otherwise stated
                     Note:
                             The notes for gtzero apply here as well.  Replace gtzero
                         with ascend while reading those notes.
    Return:
            Returns the sorted structure
    '''
    how = kwargs.get('ascend',True)
    gtzero = kwargs.get('gtzero',False)
    failValue = getFailReturn(iItem)
    if debug:
        origin = inspect.stack()[1][3]
    if not isIterable(iItem):
        if debug:
            CCprint('The iItem passed is not an iterable',origin)
        return failValue
    elif isinstance(iItem,(list,tuple)):
        if debug:
            CCprint('{} type is not supported for this function'.format(type(iItem)),origin)
        return failValue
    elif isinstance(iItem,np.ndarray) and len(iItem.dtype) == 0:
        if debug:
            CCprint('You passed a non-structured array, which is not permitted',origin)
        return failValue
    #Never assume competence.
    if isIterable(fieldnames) and isIterable(how):
        if len(fieldnames) != len(how):
            if debug:
                CCprint('Length of fieldnames and ascend kwarg need to be the same',origin)
            return failValue
    elif isIterable(fieldnames) and not isIterable(how):
        how = [how]*len(fieldnames)
    elif not isIterable(fieldnames) and isIterable(how):
        how = how[0]
    if isIterable(fieldnames) and isIterable(gtzero):
        if len(fieldnames) != len(gtzero):
            if debug:
                CCprint('Length of fieldnames and gtzero kwarg need to be the same',origin)
            return failValue
    elif isIterable(fieldnames) and not isIterable(gtzero):
        gtzero = [gtzero]*len(fieldnames)
    elif not isIterable(fieldnames) and isIterable(gtzero):
        gtzero = gtzero[0]
    #Should be safe to turn iItem to dataframe now, even if it isn't 1 of the 3 things we expect
    oItem = pd.DataFrame(iItem)
    if isIterable(fieldnames):
        if not set(fieldnames).issubset(set(oItem)):
            if debug:
                CCprint('One of the fields passed was not in the item passed',origin)
            return failValue
        for field,gt in zip(fieldnames,gtzero):
            if gt and oItem[field].dtype.kind in ['i','u','f']:
                oItem = oItem[oItem[field]>0]
    elif fieldnames not in oItem:
        if debug:
            CCprint('Field:"{}" was not in the item passed'.format(fieldnames),origin)
        return failValue
    elif gtzero and oItem[fieldnames].dtype.kind in ['i','u','f']:
        oItem = oItem[oItem[fieldnames]>0]
    oItem.sort_values(by=fieldnames,ascending=how,inplace=True)
    if isinstance(iItem,np.ndarray):
        return np.array(oItem.to_records(index=False),dtype=iItem.dtype)
    elif isinstance(iItem,dict):
        return handleMixedDictTypes(iItem,oItem.to_dict(orient='list'))
    elif isinstance(iItem,pd.DataFrame):
        return oItem.reset_index(drop=True)
    else:
        if debug:
            CCprint('You passed something that was not accounted for of type {}'.format(type(iItem)),origin)
        return oItem.reset_index(drop=True)

def SetOperations(iItem1,iItem2,**kwargs):
    '''
    Returns the set operation of things in iItem1 and iItem2.
    by default it will find the intersection
    Input:
            iItem1 - iterable (list,tuple,dict,strucarray,dataframe)
            iItem2 - iterable (list,tuple,dict,strucarray,dataframe)
    Kwargs:
            how -   "intersect" - finds intersection
                    "difference"- finds items in iItem2 that are NOT in iItem1
                    more to come
    Return:
            Returns the intersection of items as the same type as iItem2
    '''
    how = kwargs.get('how','intersect')
    failValue = getFailReturn(iItem2)
    if debug:
        origin = inspect.stack()[1][3]
    if not isIterable(iItem1) or not isIterable(iItem2):
        if debug:
            CCprint('The items you passed are not both iterable.')
        return failValue
    if (isinstance(iItem1,(list,tuple)) or (isinstance(iItem1,np.ndarray) and len(iItem1.dtype)==0 and iItem1.ndim==1)) and\
        (isinstance(iItem2,(list,tuple)) or (isinstance(iItem2,np.ndarray) and len(iItem2.dtype)==0 and iItem2.ndim==1)):
        rtype = type(iItem2)
        if isinstance(how,basestring) and how.lower() == 'intersect':
            if rtype == np.ndarray:
                return np.array(list(set(iItem2)&set(iItem1)),dtype=iItem2.dtype)
            else:
                return rtype(set(iItem2) & set(iItem1))
        elif isinstance(how,basestring) and how.lower() == 'difference':
            if rtype == np.ndarray:
                return np.array(list(set(iItem2)-set(iItem1)),dtype=iItem2.dtype)
            else:
                return rtype(set(iItem2) - set(iItem1))
        else:
            if debug:
                CCprint('The how kwarg you passed:{} was unrecognized'.format(how),origin)
            return failValue
    #Should be safe to turn iItem1 and iItem2 into dataframes
    oItem1 = pd.DataFrame(iItem1)
    oItem2 = pd.DataFrame(iItem2)
    if not set(oItem2)&set(oItem1):
        if debug:
            CCprint('None of the column names match.',origin)
        return iItem2
    if isinstance(how,basestring) and how.lower() == 'intersect':
        oItem = oItem2.merge(oItem1,indicator = True, how='left').loc[lambda x : x['_merge']=='both'].drop(columns='_merge')
    elif isinstance(how,basestring) and how.lower() == 'difference':
        oItem = oItem2.merge(oItem1,indicator = True, how='left').loc[lambda x : x['_merge']!='both'].drop(columns='_merge')
    else:
        if debug:
            CCprint('The how kwarg you passed:{} was unrecognized'.format(how),origin)
        return failValue
    if isinstance(iItem1,(dict,np.ndarray,pd.DataFrame)) and isinstance(iItem2,dict):
        return handleMixedDictTypes(iItem2,oItem[oItem2.columns].to_dict(orient='list'))
    elif isinstance(iItem1,(dict,np.ndarray,pd.DataFrame)) and isinstance(iItem2,np.ndarray):
        return np.array(oItem[oItem2.columns].to_records(index=False),dtype=iItem2.dtype)
    elif isinstance(iItem1,(dict,np.ndarray,pd.DataFrame)) and isinstance(iItem2,pd.DataFrame):
        return oItem[oItem2.columns].reset_index(drop=True)
    else:
        if debug:
            CCprint('You passed something that was not accounted for of type1 {} and type2 {}'.format(type(iItem1),type(iItem2)),origin)
        return oItem[oItem2.columns].reset_index(drop=True)

def FilterOnField(iItem, fieldname, logical, value='',**kwargs):
    '''
    Returns the filtered structure based off a fieldname and a value.  For
    dataframes, it does not reset the index.

    Input:
            iItem - dictionary, stuctured array, or dataframe
            fieldname - string of the column you want to filter
            logical - Comparison logicals [==,<,<=,>,>=,<>,!=,nonan]
                      Where nonan will get rid of all np.nan values! No value
                      needs to be passed with nonan logical
            value - value or list of values in which to filter
    Kwargs:
            return_index - False = Returns nothing
                           True = Returns the bool array of the filter for dictionaries
                           and structured arrays.  For dataframes, returns indexecies
                           that survived the filtering only.
    Return:
            Returns the filtered structure.
    '''
    ridx = kwargs.get('return_index',False)
    failValue = getFailReturn(iItem)
    if debug:
        origin = inspect.stack()[1][3]
    if not isIterable(iItem):
        if debug:
            CCprint('The iItem passed is not an iterable',origin)
        return failValue
    elif isinstance(iItem,(list,tuple)):
        if debug:
            CCprint('{} type is not supported for this function'.format(type(iItem)),origin)
        return failValue
    elif isinstance(iItem,np.ndarray) and len(iItem.dtype) == 0:
        if debug:
            CCprint('You passed a non-structured array, which is not permitted',origin)
        return failValue
    #Should be safe to turn iItem into a dataframe
    oItem = pd.DataFrame(iItem)
    if logical not in ['==','<','<=','>','>=','<>','!=','nonan']:
        if debug:
            CCprint('Unrecognized logical:{}'.format(logical),origin)
        return failValue
    if isIterable(fieldname):
        if debug:
            CCprint('Field should not be an iterable.',origin)
        return failValue
    elif not fieldname in oItem:
        if debug:
            CCprint('Field:{} was not in the passed item'.format(fieldname),origin)
        return failValue
    if isIterable(value):
        #This only makes sense if logical is in ['==','!=','<>']
        value = [handleValue(oItem,fieldname,val) for val in value]
        if logical in ['==']:
            idx = oItem[fieldname].isin(value)
            oItem = oItem[idx]
        elif logical in ['!=','<>']:
            idx = ~oItem[fieldname].isin(value)
            oItem = oItem[idx]
        else:
            if debug:
                CCprint('Unsupported logical:{} for multiple values'.format(logical),origin)
            return failValue
    else:
        value = handleValue(oItem,fieldname,value)
        #Stolen from Hamilton.... This is smart.
        if logical not in ['nonan']:
            idx = eval('oItem[fieldname]{}value'.format(logical))
            oItem = oItem[idx]
        else:
            idx = oItem[fieldname].notnull()
            oItem = oItem[idx]
    if isinstance(iItem,np.ndarray):
        if ridx:
            return np.array(oItem.to_records(index=False),dtype=iItem.dtype),idx
        else:
            return np.array(oItem.to_records(index=False),dtype=iItem.dtype)
    elif isinstance(iItem,dict):
        if ridx:
            return handleMixedDictTypes(iItem,oItem.to_dict(orient='list')),idx
        else:
            return handleMixedDictTypes(iItem,oItem.to_dict(orient='list'))
    elif isinstance(iItem,pd.DataFrame):
        if ridx:
            return oItem,oItem.index
        else:
            return oItem.reset_index(drop=True)
    else:
        if debug:
            CCprint('You passed something that was not accounted for of type {}'.format(type(iItem)),origin)
        if ridx:
            return oItem,oItem.index
        else:
            return oItem

def FilterOnIdx(iItem,idx,**kwargs):
    '''
    Returns a filtered structure based on a bool array or a list of indecies.

    Input:
            iItem - Dictionary, structured array, or pandas dataframe
            idx - a bool array that must be same length of iItem.  Or a np.array
            of index numbers to keep.
            For example:
                iItem  = {'That':[1,2,3,4,5]}
                idx = np.array(['True','False','False','False','True'])
                results = {'That':[1,5]}

                Or
                iItem = {'That':[1,2,3,4,5]}
                idx = np.array([0,4])
                results = {'That':[1,5]}
    Kwargs:
            N/A
    Return:
            Returns the filtered structure on the given idx.
    '''
    failValue = getFailReturn(iItem)
    if debug:
        origin = inspect.stack()[1][3]
    if not isIterable(iItem):
        if debug:
            CCprint('The iItem passed is not an iterable',origin)
        return failValue
    elif isinstance(iItem,(list,tuple)):
        if debug:
            CCprint('{} type is not supported for this function'.format(type(iItem)),origin)
        return failValue
    elif isinstance(iItem,np.ndarray) and len(iItem.dtype) == 0:
        if debug:
            CCprint('You passed a non-structured array, which is not permitted',origin)
        return failValue
    #Should be safe to turn iItem into dataframe
    oItem = pd.DataFrame(iItem)
    #TODO Maybe don't assume idx is numpy idx
    if idx.dtype.kind == 'b':
        if len(idx) != oItem.shape[0]:
            if debug:
                CCprint('Length of idx and iItem must be the same if you are passing a bool array',origin)
            return failValue
        oItem = oItem[idx]
    else:
        oItem = oItem.iloc[idx]
    if isinstance(iItem,np.ndarray):
        return np.array(oItem.to_records(index=False),dtype=iItem.dtype)
    elif isinstance(iItem,dict):
        return handleMixedDictTypes(iItem,oItem.to_dict(orient='list'))
    elif isinstance(iItem,pd.DataFrame):
        return oItem.reset_index(drop=True)
    else:
        if debug:
            CCprint('You passed something that was not accounted for of type {}'.format(type(iItem)),origin)
        return oItem.reset_index(drop=True)

def UniqueOnField(iItem,fieldname,**kwargs):
    '''
    Returns a structured array with only unique values from the fieldname passed.

    Input:
            iItem - Dictionary, structured array, or dataframe
            fieldname - string of the column name you wish to unique
    Kwargs:
        sort - True- Sort structure
               False = Don't sort
        ascend - True = If sort: Sort ascending order
                 False - If sort: Sort descending order
        keep - 'first' = keep first instance found while taking uniques
               'last' = keep last instance found while taking uniques
    '''
    sort = kwargs.get('sort',True)
    how = kwargs.get('ascend',True)
    keep = kwargs.get('keep','first')
    failValue = getFailReturn(iItem)
    if debug:
        origin = inspect.stack()[1][3]
    if not isIterable(iItem):
        if debug:
            CCprint('The iItem passed is not an iterable',origin)
        return failValue
    elif isinstance(iItem,(list,tuple)):
        if debug:
            CCprint('{} type is not supported for this function'.format(type(iItem)),origin)
        return failValue
    elif isinstance(iItem,np.ndarray) and len(iItem.dtype) == 0:
        if debug:
            CCprint('You passed a non-structured array, which is not permitted',origin)
        return failValue
    #Should be safe to turn iItem into dataframe
    oItem = pd.DataFrame(iItem)
    if not fieldname in oItem:
        if debug:
            CCprint('Field:{} was not in the passed item'.format(fieldname),origin)
        return failValue
    oItem.drop_duplicates(subset=fieldname,keep=keep,inplace=True)
    if sort:
        oItem.sort_values(by=fieldname,ascending=how,inplace=True)
    if isinstance(iItem,np.ndarray):
        return np.array(oItem.to_records(index=False),dtype=iItem.dtype)
    elif isinstance(iItem,dict):
        return handleMixedDictTypes(iItem,oItem.to_dict(orient='list'))
    elif isinstance(iItem,pd.DataFrame):
        return oItem.reset_index(drop=True)
    else:
        if debug:
            CCprint('You passed something that was not accounted for of type {}'.format(type(iItem)),origin)
        return oItem.reset_index(drop=True)

#This is a map from the old functionmatlab functions to these
SortByField = SortFields
SortByField_NP = SortFields
setdiff = partial(SetOperations, how='difference')
intersect = partial(SetOperations, how='intersect')
SortOnField = partial(FilterOnField,logical='==')

SortOnField_NP = partial(FilterOnField,logical='==')
SortOnLogical = FilterOnField
RemoveOnField = partial(FilterOnField,logical='!=')
RemoveOnField_NP = partial(FilterOnField,logical='!=')
RemoveOnNaN_NP = partial(FilterOnField,logical='nonan',value='')
filterStruct = FilterOnIdx
fiterStructMixed = FilterOnIdx
ReturnUniqueStructure = UniqueOnField
ReturnUniqueStructure_NP = UniqueOnField


if __name__ == '__main__':
    #TEST for each of them

    #mock data for testing
    strucarray1 = np.array([(45, 1., 'mars', 1, 1.), (67, 1., 'pluto', 1, 1.),
           (12, 1., 'saturn', 1, 1.)],
          dtype=[('f0', '<i4'), ('f1', '<f4'), ('f2', '<U10'), ('f3', '<i4'), ('f4', '<f4')])
    strucarray2 = np.array([(45, 1., 'mars', 1, 2.), (33, 3., 'venus', 1, 1.),
           (123, 13., 'jupiter', 12, 12.)],
          dtype=[('f0', '<i4'), ('f1', '<f4'), ('f2', '<U10'), ('f3', '<i4'), ('f4', '<f4')])

    x = OrderedDict({'this':(0,1,6,4,5,6,-7),
         'that':np.array([5,4,3,6,7,8,-3]),
         'wbb':np.array(['what','is','this','sentence','that','i','am'])})
    xx = {'this':np.array([1,3,2,3,4,np.nan])}

    z = {'ghost':[1,2,4],'weeze':[0,3,2],'woop':['this','that',np.nan],'this':[2,1,3]}


#    output = UniqueOnField(x,'this',sort=True)
    output = intersect(xx,x)

    #y = SortOnField(strucarray,'f0',[45,67])
#    y = intersect(x,xx)
