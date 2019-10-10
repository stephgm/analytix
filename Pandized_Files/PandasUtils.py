#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Oct  8 18:46:27 2019

@author: Jordan Marlow

Pandas Utils.  This file takes out some of the guess work for Pandas functions
and tries to optimize different ways of using Pandas.  These functions only work for DataFrames at
the moment.
"""

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

def isStructure(iItem,**kwargs):
    '''
    Returns whether the iItem is considered a structure by our definition
    '''
    return isinstance(iItem,(pd.DataFrame,dict)) or (isinstance(iItem,np.ndarray) and len(iItem.dtype)>0)


def MapColumns(iItem1,iItem2,mapcols='',left_on='index',right_on='index',**kwargs):
    '''
    This function takes two dataframes and maps columns from iItem2 to iItem1
    based on one column from the iItem1 and one from iItem2.  This is like a merge,
    but doesn't overpopulate the dataframe with nans.

    Input:
            iItem1 - dataframe in which you want to map columns to.
            iItem2 - dataframe in which you want to map columns from
            mapcols - The column or list of columns to map from iItem2 onto iItem1
            left_on - The column used for matching values with right_on.  This column is in iItem1
            right_on - The column used for matching values with left_on.  This column is in iItem2

    Kwargs:
            fillna - Value that you want to fill NANs with.
            allcols - True:  Will grab all columns from iItem2 and map them to iItem1.  All columns
                        are gathered except for right_on
                      False: Will use mapcols instead.
    '''
    fillna = kwargs.get('fillnan','UNK')
    allcols = kwargs.get('allcol',False)
    failValue = getFailReturn(iItem1)
    if debug:
        origin = inspect.stack()[1][3]
    if not (isinstance(iItem1,pd.DataFrame) and isinstance(iItem2,pd.DataFrame)):
        if debug:
            CCprint('One of the passed items is not a structure',origin)
        return failValue
    if not isIterable(mapcols):
        mapcols = [mapcols]

    oItem1 = pd.DataFrame(iItem1)
    oItem2 = pd.DataFrame(iItem2)

    if allcols:
        mapcols = list(oItem2)
        if right_on in mapcols:
            mapcols.pop(mapcols.index(right_on))
    if mapcols and not set(list(mapcols)).issubset(set(oItem2.columns)):
        if debug:
            CCprint('Field:{} not in iItem2'.format(mapcols),origin)
        return failValue

    if not (left_on in oItem1 and right_on in oItem2):
        if debug:
            CCprint('Either {} not in iItem1 or {} not in iItem2'.format(left_on,right_on),origin)
        return failValue

    oItem2.set_index(right_on,inplace=True)

    for col in mapcols:
        if col in oItem1:
            lcol = '{}_right'.format(col)
        else:
            lcol = col
        if not fillna:
            oItem1[lcol] = oItem1[left_on].map(oItem2[col])
        else:
            oItem1[lcol] = oItem1[left_on].map(oItem2[col]).fillna(fillna)
    return oItem1

def RunningTotal(iItem,StartTimefld,EndTimefld='',**kwargs):
    '''
    If StartTimefld and EndTimefld given:

    Takes in a dataframe with Start Times and End Times of some object to keep a
    Running total of.  This function only needs the times, as it is just counting.
    This works by taking in the Spawn times and Termination times of objects.  This
    function Checks that the start times happen before the end times.  If not, then it will
    give a message to the user.  Two more dataframes are created, one with the StartTimes
    another with the Endtimes.  A new column is added to each of these dataframes, called
    ObjValue.  The start times ObjValue = 1 because an object is being added.  The end times
    ObjValue = -1 because an object is being terminated.  After these fields are added
    the two dataframes are concatenated and sorted by the Time.  That way everything is happening
    in order.  A cumulative sum is taken of the ObjValue field.  This gives the total number
    of objects present at a specific time.  Lastly any duplicate times are dropped, but the last
    of these are kept because that is the resulting sum after that instance of time
    has passed.

    If only StartTimefld given:

    Takes in dataframe with Spawning times of objects.  This will do a time sort
    of the dataframe on the StartTimefld.  Will then give each item an ObjValue = 1
    because in this mode you are only considering a cumulative total of objects
    that were spawned over the time interval.  Duplicate times are dropped after
    the cumulative sum is taken, that way it has only one resulting sum after a
    particular instance of time.

    Input:
            iItem - pandas dataframe
            StartTimefld - The field that represents spawn time of object
            EndTimefld - The field that represents termination time of object.
                         This value does not have to be set if you only want total
                         objects over time
    Kwargs:
            reset - Bool to reset index or not.  Default True.
    Return:
            Returns a dataframe with the fields Time and Total.
    '''
    reset = kwargs.get('reset',True)
    if debug:
        origin = inspect.stack()[1][3]
    failValue = getFailReturn(iItem)
    if not isinstance(iItem,pd.DataFrame):
        if debug:
            CCprint('iItem is not a dataframe',origin)
        return failValue
    if EndTimefld:
        iItem1 = pd.DataFrame()
        iItem2 = pd.DataFrame()
        if not (StartTimefld in iItem and EndTimefld in iItem):
            if debug:
                CCprint('The fields passed are not in the passed dataframe')
            return failValue
        if not iItem[StartTimefld].dtype.kind in ['i','u','f']:
            try:
                iItem[StartTimefld] = iItem[StartTimefld].astype(float)
            except:
                if debug:
                    CCprint('Could not convert Start Time field to float.  Returning empty')
                return failValue
        if not iItem[EndTimefld].dtype.kind in ['i','u','f']:
            try:
                iItem[EndTimefld] = iItem[EndTimefld].astype(float)
            except:
                if debug:
                    CCprint('Could not convert End Time field to float. Returning empty')
                return failValue
        idx = iItem[StartTimefld] > iItem[EndTimefld]
        if idx.all():
            if debug:
                CCprint('It seems like your StartTimes and EndTimes are swapped, as all End times < Start Times.  Swapping')
            StartTimefld,EndTimefld = EndTimefld,StartTimefld
        elif idx.any():
            if debug:
                CCprint('Some of the End times are before the Start times.  Not physical, but may still look physical, which is wrong.')
        iItem1['Time'] = iItem[StartTimefld]
        iItem2['Time'] = iItem[EndTimefld]
        iItem1['ObjValue'] = pd.Series([1]*iItem1.shape[0])
        iItem2['ObjValue'] = pd.Series([-1]*iItem2.shape[0])
        oItem = pd.concat([iItem1,iItem2])
    else:
        if not StartTimefld in iItem:
            if debug:
                CCprint('Field:{} not in iItem'.format(StartTimefld),origin)
            return failValue
        oItem = pd.DataFrame()
        oItem['Time'] = iItem[StartTimefld]
        oItem['ObjValue'] = pd.Series([1]*iItem.shape[0])
    oItem.sort_values('Time',inplace=True)
    oItem['Total'] = oItem['ObjValue'].cumsum()
    oItem.drop(['ObjValue'],inplace=True,axis='columns')
    oItem.drop_duplicates('Time',keep='last',inplace=True)
    if reset:
        oItem = oItem.reset_index(drop=True)
    return oItem



def SplitDataFrameOnUnique(iItem,FieldName,**kwargs):
    '''
    Returns a dictionary of dataframes that only have unique values of the specified
    fieldname.  This will condense code so that you don't have to write out
    alot of filtering calls.  If you only need a few of these dataframes, it is
    probably better to use FilterOnField on StructureUtils.py or just pop out
    the items you don't need from the dictionary returned from this function.

    Input:
            iItem - dataframe
            FieldName - Field that is in the dataframe
    Kwargs:
            reset - Bool to reset the index.  Default is True
    Return:
            Returns dictionary of dataframes with the key = to the unique value.
            The key is also the same type as the pandas column.  So, not necessarily
            a string key will get passed back.
    '''
    reset = kwargs.get('reset',True)
    if debug:
        origin = inspect.stack()[1][3]
    if not isinstance(iItem,pd.DataFrame):
        if debug:
            CCprint('The input item is not a dataframe.',origin)
        return {}

    if FieldName not in iItem:
        if debug:
            CCprint('Field:{} is not in the dataframe',origin)
        return {}
    oItem = {}
    uniquevals = pd.unique(iItem[FieldName])
    for val in uniquevals:
        oItem[val] = iItem[iItem[FieldName]==val]
        if reset:
            oItem[val].reset_index(drop=True)
    return oItem


if __name__ == '__main__':
    truth = {'TrackId':[1,2,3,4,5,5],
             'Those':[1,2,3,4,5,6]}
    track = {'TrackId':[1,2,3,4,6,7,8,11,0,10],
             'Type':['Puppy','Doggy','Tnak','TV','Fun','Hank','tank','pid','Unicorn','pid'],
             'Type2':[5,55,555,5555,55555,555555,5555555,55555555,555555555,55555555555],
             'Those':[1,2,3,4,5,10,44,333,444,11]}

    Truth = pd.DataFrame(truth)
    Track = pd.DataFrame(track)
    x = pd.merge(Truth,Track,how='inner',left_on='TrackId',right_on='TrackId')
    xx = pd.merge(Truth,Track,how='outer',left_on='TrackId',right_on='TrackId')
    xxx = xx.drop_duplicates('TrackId')

    y = MapColumns(Truth,Track,'TrackId','Those','Those',allcol=False)

    import matplotlib.pyplot as plt
    #simple example
    #As soon as one object gets terminated, another is spawned.  Should show 1 until end.
    Obj = {'StartTalo':[0,1,2,3,4,5,6,7],
           'EndTalo':[1,2,3,4,5,6,7,8]}

    arraysize = 50000
    #complex example
    #but may not be physical in the sense that some of the objects made this way
    #have a chance to End before they begin, but the time offset is there to offset that.

    #Should be only increasing up til 400 seconds.  This is where objects start to terminate.
    #After that the line might look to be steadily decreasing, however, there could
    #still be objects spawning.  Just zoom in to see.  The more points plotted
    #The more linear these will look.


    Obj = {'StartTalo':np.random.uniform(0,750,arraysize),
           'EndTalo':np.random.uniform(400,800,arraysize)}



    #Does 5million objects in about 9 seconds on my laptop....

    obj = pd.DataFrame(Obj)
    import time
    start = time.time()
    x = RunningTotal(obj,'StartTalo')
    end = time.time()
    print end-start
    plt.plot(x['Time'],x['Total'])
