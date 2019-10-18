#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 20 23:37:07 2019

@author: Jordan
"""
'''This file is a group of functions that are commonly used in Phobos'''
import os
import sys
import glob
import h5py
import fnmatch
import pandas as pd
import numpy as np
import cPickle as pickle
from collections import Iterable
from six import string_types

debug = True

if True:
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
### Data Getting

    def thin_data(array,pct,**kwargs):
        '''
        Returns a thinned version of what was passed in by leaving pct% of the
        original array.

        Input:
                array - Can be list, tuple, single layer dictionary of lists or tuples,
                        numpy array, or pandas DataFrame

                pct -   The percent of data that you want to gather from array.
                        If pct > 100 will be set to 100%
                        If pct < X% where X% is the magic percentage that would give
                        you only 1 row or column, then pct = X%

                        Example:
                            thin_data([0,1,2,3,5],10) = []
                            if pct was left at 10% this return would be empty
                            since the list has 5 elements. The minimum % that would return
                            some value is 20%, thus pct will be made 20% and a message
                            will be printed alerting you of this.  The return will
                            actually be [0] in this example.

        Kwargs:
                how - either "row" or "column" for if you have sideways data.
                        if how="column" and array is a DataFrame, it will return
                        a subset of the columns!
                minrows - The minimum number of rows to return
                sortHeader - The header you want to sort on first before thinning
        Return:
                Returns the thinned array

        '''
        how = kwargs.get('how','row')
        minrows = kwargs.get('minrows',1)
        sortHeader = kwargs.get('sortHeader','')
        dtype = None
        seconddtype = None
        if not isIterable(array):
            if debug:
                print('The array passed is not iterable')
            return array
        dtype = type(array)
        if how == 'row':
            direction = 0
        elif how == 'column':
            direction = 1
        else:
            if debug:
                print('The how kwarg passed was not "row" or "column", defaulting to "row"')
            how = 'row'
            direction = 0
        if isinstance(array,(tuple,list)):
            how = 'row'
            direction = 0
        if isinstance(array,np.ndarray) and len(array.dtype) == 0:
            how = 'row'
            direction = 0
        if isinstance(pct,basestring):
            try:
                pct = float(pct)
            except:
                if debug:
                    print('Could not convert pct:{} to a float. Returning input')
                return array
        if not isinstance(minrows,int):
            try:
                minrows = int(minrows)
            except:
                if debug:
                    print('Could not convert minrows kwarg to int.  Returning input')
                return array
        #Should be safe to turn into dataframe
        oArray = pd.DataFrame(array)
        if sortHeader and sortHeader in oArray:
            oArray = oArray.sort_values(sortHeader)
        else:
            if debug:
                print('{} not in the passed iterable.  Or you passed a list, tuple, or non-structured array'.format(sortHeader))
        if pct >= 100:
            return array
        elif pct*.01*oArray.shape[direction] < minrows:
            suggested = minrows*100./oArray.shape[direction]
            if debug:
                print('The percent of data you are trying to get {}%, will likely make your returned data empty. Returning {}%, this should just be {} {}.'.format(pct,suggested,minrows,how))
            pct = suggested
        newindex = np.linspace(0,oArray.shape[direction]-1,int(oArray.shape[direction]*.01*pct),dtype=int)
        if direction == 0:
            oArray = oArray.iloc[newindex].reset_index(drop=True)
        elif direction == 1:
            oArray = oArray.iloc[:,newindex].reset_index(drop=True)

        if isinstance(array,(tuple,list)):
            print oArray
            return dtype(oArray[list(oArray)[0]].to_list())
        elif isinstance(array,dict):
            return handleMixedDictTypes(array,oArray.to_dict(orient='list'))
        elif isinstance(array,np.ndarray) and len(array.dtype) > 0:
            return np.array(oArray.to_records,dtype=array.dtype)
        elif isinstance(array,np.ndarray):
            return np.array(oArray[0].to_list(),dtype=array.dtype)
        elif isinstance(array,pd.DataFrame):
            return oArray
        else:
            return array


#    def thin_data(array,pct,**kwargs):
#
#        how = kwargs.get('how','row')
#        minrows = kwargs.get('minrows',1)
#        sortHeader = kwargs.get('sortHeader','')
#        dtype = None
#        seconddtype = None
#        if not isinstance(array,pd.DataFrame) and not isinstance(array,np.ndarray):
#            if debug:
#                print('The data you entered was not a dataframe nor a numpy array.  Trying to convert and pass back the type you gave me. Setting how="row"')
#            if isinstance(array,Iterable) and not isinstance(array,basestring):
#                dtype = type(array)
#                if isinstance(array,dict):
#                    if debug:
#                        print('You passed in a dictionary, attempting to make it a DataFrame.  If it is nested, then your guess is as good as mine as to how it will work.  Setting how="row"')
#                    try:
#                        seconddtype = type(array[array.keys()[0]])
#                        array = pd.DataFrame(array)
#                        how = 'row'
#                    except:
#                        if debug:
#                            print('The conversion of the dictionary to dataframe failed. Returning input')
#                        return array
#                else:
#                    try:
#                        array = np.array(array)
#                        how = 'row'
#                    except:
#                        if debug:
#                            print('The conversion to a numpy array was not possible! Returning input')
#                        return array
#            else:
#                if debug:
#                    print('The array that you passed is not Iterable or it is a string, which cannot be made into a numpy array. Returning input')
#                return array
#        if isinstance(pct,basestring):
#            try:
#                pct = float(pct)
#            except:
#                if debug:
#                    print('Could not convert pct:{} to a float. Returning input')
#                return array
#        if how == 'row':
#            direction = 0
#        elif how == 'column':
#            direction = 1
#        else:
#            if debug:
#                print('How should either be "row" or "column", you entered {}.  Assuming you mean "row" because I can.'.format(how))
#            direction = 0
#        if not isinstance(minrows,int):
#            try:
#                minrows = int(minrows)
#            except:
#                if debug:
#                    print('Could not convert minrows kwarg to int.  Returning input')
#                return array
#        if pct >= 100:
#            return array
#        elif pct*.01*array.shape[direction] < minrows:
#            suggested = minrows*100./array.shape[direction]
#            if debug:
#                print('The percent of data you are trying to get {}%, will likely make your returned data empty. Returning {}%, this should just be {} {}.'.format(pct,suggested,minrows,how))
#            pct = suggested
#        newindex = np.linspace(0,array.shape[direction]-1,int(array.shape[direction]*.01*pct),dtype=int)
#        if dtype != None and isinstance(array,np.ndarray):
#            if sortHeader:
#                if array.dtype.names != None and sortHeader in array.dtype.names:
#                    array = np.sort(array,order=sortHeader)
#            array = array[newindex]
#            array = dtype(array)
#            return array
#        elif dtype != None and isinstance(array,pd.DataFrame):
#            array = array.iloc[newindex].reset_index(drop=True)
#            array = array.to_dict(orient='list')
#            for key in array:
#                array[key] = seconddtype(array[key])
#            return array
#        elif isinstance(array,pd.DataFrame):
#            if how == 'row':
#                array = array.iloc[newindex].reset_index(drop=True)
#            else:
#                array = array.iloc[:,newindex].reset_index(drop=True)
#            return array
#        elif isinstance(array,np.ndarray):
#            array = array[newindex]
#            return array
#        else:
#            return array

    def get_h5_attributes(fpath,**kwargs):
        '''
        Returns a dictionary of dataframes of attributes.  Will only return items in which
        attributes are found.
        Input:
                fpath - the absolute path to the .h5 file
        Kwargs:
                grp - The group name that you want to check for attributes
                dset - The dataset name that you want to check for attributes
                addDset - Add dataset name column to the Dataframe
                addGrp - Add Group name column to the dataframe
                addFile - Add File name column to dataframe
                addCustom - Add user specified identifier to dataframe
        Return:
                {file: file attribute Dataframe,
                Kwargs: Kwarg attributes Dataframe}

                Note:  This can be empty.
        '''
        data = {}
        grp = kwargs.get('grp',None)
        dset = kwargs.get('dset',None)
        addDset = kwargs.get('addDset',False)
        addGrp = kwargs.get('addGrp',False)
        addFile = kwargs.get('addFile',False)
        addCustom = kwargs.get('addCustom',{})

        if os.path.isfile(fpath):
            with h5py.File(fpath,'r') as hf:
                data['file'] = pd.DataFrame({k:v for k,v in hf.attrs.iteritems()})
                if grp and grp in hf:
                    data['grp'] = pd.DataFrame({k:v for k,v in hf[grp].attrs.iteritems()})
                    if dset and dset in hf[grp]:
                        data['dset'] = pd.DataFrame({k:v for k,v in hf[grp][dset].attrs.iteritems()})
                    else:
                        if debug:
                            print('{} is not in the h5 file {}, ommiting'.format(dset,fpath))
                else:
                    if debug:
                        print('{} is not in the h5 file {}, omitting'.format(grp,fpath))
            for key in data.keys():
                if data[key].shape[0] == 0:
                    data.pop(key)
            if addDset and dset:
                for key in data:
                    data[key]['Dset'] = np.array([dset]*data[key].shape[0])
            if addGrp and grp:
                for key in data:
                    data[key]['Group'] = np.array([grp]*data[key].shape[0])
            if addFile:
                for key in data:
                    data[key]['File'] = np.array([os.path.basename(fpath)]*data[key].shape[0])
            if addCustom and isinstance(addCustom,dict):
                for key in data:
                    for custom in addCustom:
                        data[key][custom] = np.array([addCustom[custom]]*data[key].shape[0])
        else:
            if debug:
                print('{} is not a valid file'.format(fpath))
        return data

    def get_h5_data(fpath,grp,dset,**kwargs):
        '''
        Given a filepath, group, and dataset for an h5 file, this function
        returns the data in a pandas dataframe
        Input:
                fpath - the file path to the h5 file
                group - the group in the h5 file
                dset - the dataset inside the group of the h5 file
        Kwargs:
                headers - a list of headers to extract from the h5 dataset
                section - tuple indicating the slice of the data to return (0,10) -> [0:10]
                addDset - adds a Dataset name column to the dataframe
                addGrp - add a Group name column to the dataframe
                addFile - adds a Filename column to the dataframe
                addCustom - adds a user specified identifier to the dataframe
                gatherpct - a float X that will gather X% of the data
                sortHeader - a header to sort on in ascending order
                Phobos - Tells function to return fpath and dataframe
            Note:  You can apply both a section and gatherpct and will work as expected

        Return:
                Returns pandas dataframe of the data from the h5 file
        '''
        data = {}
        headers = kwargs.get('headers',None)
        section = kwargs.get('section',None)
        addDset = kwargs.get('addDset',False)
        addGrp  = kwargs.get('addGrp',False)
        addFile = kwargs.get('addFile',False)
        addCustom = kwargs.get('addCustom',{})
        gatherpct = kwargs.get('gatherpct',100)
        sortHeader = kwargs.get('sortHeader','')
        Phobos = kwargs.get('Phobos',False)
        if section:
            if isinstance(section,basestring):
                if debug:
                    print('The section kwarg you passed is a string.  Pass an iterable')
                section = (0,200)
            elif isinstance(section,Iterable) and len(section) < 2:
                if debug:
                    print('The section kwarg you passed is not a correct length.')
                section = (0,200)
            elif isinstance(section,Iterable) and (not isinstance(section[0],int) or not isinstance(section[1],int)):
                if debug:
                    print('One or both of the indecies in the section kwarg you passed are not integers')
                section = (0,200)
            elif not isinstance(section,Iterable):
                if debug:
                    print('The section kwarg you passed is not an iterable')
                section = (0,200)
        if headers and not isinstance(headers,Iterable) and not isinstance(headers,basestring):
            if debug:
                print('The headers Kwarg you passed is not iterable.  Gathering all data')
            headers = None
        elif headers:
            if not isinstance(headers[0],basestring):
                headers = None
                if debug:
                    print('The iteration items of the headers Kwarg are not strings. Gathering all Data')

        if not os.path.isfile(fpath):
            if debug:
                print('{} is not a valid file'.format(fpath))
            return pd.DataFrame()
        with h5py.File(fpath,'r') as hf:
            if grp in hf:
                if dset in hf[grp]:
                    if headers:
                        getheaders=headers
                        if sortHeader and sortHeader not in getheaders:
                            getheaders.append(sortHeader)
                    else:
                        if isinstance(hf[grp][dset],h5py.Dataset):
                            getheaders=hf[grp][dset].dtype.fields.keys()
                        else:
                            getheaders=hf[grp][dset].keys()
                    if isinstance(hf[grp][dset],h5py.Dataset):
                        if isinstance(section,tuple):
                            data = {header:hf[grp][dset][header][section[0]:section[1]] for header in getheaders if header in hf[grp][dset].dtype.fields.keys()}
                        else:
                            data = {header:hf[grp][dset][header][...] for header in getheaders if header in hf[grp][dset].dtype.fields.keys()}
                    else:
                        if isinstance(section,tuple):
                            data = {header:hf[grp][dset][header][section[0]:section[1]] for header in getheaders if header in hf[grp][dset].keys() and isinstance(hf[grp][dset][header],h5py.Dataset)}
                        else:
                            data = {header:hf[grp][dset][header][...] for header in getheaders if header in hf[grp][dset].keys() and isinstance(hf[grp][dset][header],h5py.Dataset)}
                else:
                    if debug:
                        print('{} dataset is not in {}'.format(dset,fpath))
                    return pd.DataFrame()
            else:
                if debug:
                    print('{} group is not in {}'.format(grp,fpath))
                return pd.DataFrame()

        if addDset:
            data['Dset'] = np.array([dset]*len(data[data.keys()[0]]))
        if addGrp:
            data['Group'] = np.array([grp]*len(data[data.keys()[0]]))
        if addFile:
            data['File'] = np.array([os.path.basename(fpath)]*len(data[data.keys()[0]]))
        if addCustom and isinstance(addCustom,dict):
            for custom in addCustom:
                data[custom] = np.array([addCustom[custom]]*len(data[data.keys()[0]]))
        y = pd.DataFrame(data)
        if sortHeader:
            if not sortHeader in y:
                if debug:
                    print('field:{} was not in headers to sort on'.format(sortHeader))
                pass
            else:
                y.sort_values(sortHeader,inplace=True)
                y.reset_index(drop=True,inplace=True)
        return thin_data(y,gatherpct)

    def get_multiple_datasets(fpath,grp,dsets,**kwargs):
        gatherpct = kwargs.get('gatherpct',100)
        dflist = []
        if not isinstance(dsets,list):
            if debug:
                print('The passed dsets arg was not a list')
            return pd.DataFrame()
        if not os.path.isfile(fpath):
            if debug:
                print('{} is not a valid file'.format(fpath))
            return pd.DataFrame()
        for dset in dsets:
            dflist.append(get_h5_data(fpath,grp,dset,gatherpct=gatherpct,addDset=True))
        return pd.concat(dflist)

    def get_multiple_groups(fpath,grps,dset,**kwargs):
        gatherpct = kwargs.get('gatherpct',100)
        dflist = []
        if not isinstance(grps,list):
            if debug:
                print('The passed grps arg was not a list')
            return pd.DataFrame()
        if not os.path.isfile(fpath):
            if debug:
                print('{} is not a valid file'.format(fpath))
            return pd.DataFrame()
        for grp in grps:
            dflist.append(get_h5_data(fpath,grp,dset,gatherpct=gatherpct,addGrp=True))
        return pd.concat(dflist)

    def get_multiple_files(fpaths,grp,dset,**kwargs):
        gatherpct = kwargs.get('gatherpct',100)
        if not isinstance(fpaths,list):
            if debug:
                print('The passed fpaths args was not a list')
            return pd.DataFrame()
        for fpath in fpaths:
            dflist.append(get_h5_data(fpath,grp,dset,gatherpct=gatherpct,addFile=True))
        return pd.concat(dflist)

    def get_multiple_everything(fpaths,grps,dsets,**kwargs):
        gatherpct = kwargs.get('gatherpct',100)
        addCustom = kwargs.get('addCustom',{})
        if not isinstance(fpaths,list):
            fpaths = [fpaths]
        if not isinstance(grps,list):
            grps = [grps]
        if not isinstance(dsets,list):
            dsets = [dsets]
        for fpath in fpaths:
            for grp in grp:
                for dset in dests:
                    dflist.append(get_h5_data(fpath,grp,dset,gatherpct=gatherpct,addFile=True,addGrp=True,addDset=True,addCustom=addCustom))
        return pd.concat(dflist)



    def get_xlsx_data(fpath,sheetname,**kwargs):
        '''
        Returns the xlsx dataframe from a particular sheet within the xlsx file given
        the absolute file path of the excel file.

        Input:
                fpath - The absolute path to the xlsx file
                sheetname - The sheetname of the data you want to read into a dataframe

        Kwargs:
                headers - a list of headers that are wanted from the sheet in the file
                gatherpct - a float X that will gather X% of the data
                Phobos - This tells the function to return fpath and dataframe

        Return:
                Returns a pandas Dataframe
        '''
        if not os.path.isfile(fpath):
            if debug:
                print('{} is not a valid file.'.format(fpath))
            return pd.DataFrame()
        gatherpct = kwargs.get('gatherpct',100)
        headers = kwargs.get('headers',None)
        addCustom = kwargs.get('addCustom',{})
        addFile = kwargs.get('addFile',False)
        addSheet = kwargs.get('addSheet',False)
        sortHeader = kwargs.get('sortHeader','')
        if headers and not isinstance(headers,Iterable) and not isinstance(headers,basestring):
            if debug:
                print('The headers Kwarg you passed is not iterable.  Gathering all data')
            headers = None
        elif headers:
            if not isinstance(headers[0],basestring):
                headers = None
                if debug:
                    print('The iteration items of the headers Kwarg are not strings. Gathering all Data')

        y = pd.read_excel(fpath,sheet_name=sheetname)
        if headers:
            if sortHeader and sortHeader not in headers:
                headers.append(sortHeader)
            y = y[headers]
        if addFile:
            y['File'] = np.array([os.path.basename(fpath)]*y.shape[0])
        if addSheet:
            y['SheetName'] = np.array([sheetname]*y.shape[0])
        if addCustom and isinstance(addCustom,dict):
            for custom in addCustom:
                y[custom] = np.array([addCustom[custom]]*y.shape[0])
        if sortHeader:
            if not sortHeader in y:
                if debug:
                    print('Field:{} was not in the dataset to be sorted on'.format(sortHeader))
                pass
            else:
                y.sort_values(sortHeader,inplace=True)
                y.reset_index(drop=True,inplace=True)
        try:
            return thin_data(y,gatherpct)
        except:
            if debug:
                print('Something went wrong while trying to thin out the data, returning un-thinned')
            return y

    def get_pickle_data(fpath,**kwargs):
        '''
        Returns the pickled dataframe from absolute file path of the pkl file.

        Input:
                fpath - The absolute path to the pkl file

        Kwargs:
                headers - a list of headers that are wanted from the sheet in the file
                gatherpct - a float X that will gather X% of the data

        Return:
                Returns a pandas Dataframe
        '''
        if not os.path.isfile(fpath):
            if debug:
                print('{} is not a valid file.'.format(fpath))
            return pd.DataFrame()
        gatherpct = kwargs.get('gatherpct',100)
        headers = kwargs.get('headers',None)
        addFile = kwargs.get('addFile',False)
        addCustom = kwargs.get('addCustom',{})
        sortHeader = kwargs.get('sortHeader','')
        if headers and not isinstance(headers,Iterable) and not isinstance(headers,basestring):
            if debug:
                print('The headers Kwarg you passed is not iterable.  Gathering all data')
            headers = None
        elif headers:
            if not isinstance(headers[0],basestring):
                headers = None
                if debug:
                    print('The iteration items of the headers Kwarg are not strings. Gathering all Data')

        y = pickle.load(file(fpath,'rb'))
        if headers:
            if sortHeader and not sortHeader in headers and sortHeader in y:
                headers.append(sortHeader)
            y=y[headers]
        if addFile:
            y['File'] = np.array([os.path.basename(fpath)]*y.shape[0])
        if addCustom and isinstance(addCustom,dict):
            for custom in addCustom:
                y[custom] = np.array([addCustom[custom]]*y.shape[0])
        if sortHeader:
            if sortHeader in y:
                if debug:
                    print('Field:{} not in the data to be sorted on.'.format(sortHeader))
                pass
            else:
                y.sort_values(sortHeader,inplace=True)
                y.reset_index(drop=True,inplace=True)
        try:
            return thin_data(y,gatherpct)
        except:
            if debug:
                print('Something went wrong while trying to thin out the data, returning un-thinned')
            return y

### Open File Attributes

    def get_groups(fpath,**kwargs):
        '''
        Function will return the groups that Phobos needs to populate GroupNameCombo.
        Will attempt to use json file to speed things along.
        Input:
                fpath - The full path to the file.
                        Supported Types = .h5
        Kwargs:
                N/A
        Return:
                Returns a list of group names
        '''
        if not os.path.isfile(fpath):
            if debug:
                print('{} is not a valid file'.format(fpath))
            return []
        extension = os.path.splitext(fpath)[-1].strip().lower()
        if extension in ['.h5','.hdf5']:
            if not os.path.isfile(fpath.split(extension)+'.json'):
                if debug:
                    print('{} does not have a json generated'.format(fpath))
                with h5py.File(fpath,'r') as hf:
                    grps = [grp for grp in hf.keys() if isinstance(hf[grp],h5py._hl.group.Group)]
                    if grps:
                        return grps
                    else:
                        return ['/']
            else:
                with open(fpath.split(extension)+'.json','rb') as jf:
                    grps = json.load(jf).keys()
                return grps
        elif extension in ['.csv','.xlsx','.pkl']:
            return ['/']
        else:
            if debug:
                print('Extension {} not supported'.format(extension))
            return []

    def get_dsets(fpath,grp,**kwargs):
        '''
        Function will return the datasets that Phobos needs to populate DatasetList
        Input:
                fpath - The full path to the file
                        Supported Types = .h5
                grp -   The group from the GroupNameCombo.  This is mainly used for h5 files
        Kwargs:
                N/A
        Return:
                Returns a list of datasets
        '''
        if not os.path.isfile(fpath):
            if debug:
                print('{} is not a valid file'.format(fpath))
            return []
        extension = os.path.splitext(fpath)[-1].strip().lower()
        if extension in ['.h5','.hdf5']:
            if not os.path.isfile(fpath.split(extension)+'.json'):
                if debug:
                    print('{} does not have a json generated'.format(fpath))
                with h5py.File(fpath,'r') as hf:
                    if grp in hf:
                        dsets = [dset for dset in hf[grp].keys()]
                        if dsets:
                            return dsets
                        else:
                            return []
                    else:
                        if debug:
                            print('Group {} is not in file {}'.format(grp,fpath))
                        return []
            else:
                with open(fpath.split(extension)+'.json','rb') as fid:
                    dsdict = json.load(fid)
                    if grp in dsdict:
                        dsets = [dset for dset in dsdict[grp] if dset not in ['commoncol','type']]
                    else:
                        if debug:
                            print('{} was not in the json file'.format(grp))
                        dsets = []
                return dsets
        elif extension in ['.csv','.pkl']:
            return ['Data']
        elif extension in ['.xlsx']:
            df = pd.read_excel(fpath)
            xls = pd.ExcelFile(fpath)
            return xls.sheet_names
        else:
            if debug:
                print('Extension {} not supported'.format(extension))
            return []

    def get_headers(fpath,grp,dset,**kwargs):
        '''
        Function will return the headers that Phobos needs to populate HeaderList
        Input:
                fpath - The full path to the file
                        Supported Types = .h5
                grp -   The group from the GroupNameCombo.  This is mainly used for h5 files
                dset -  The dataset selection from DatasetList.  This is mainly used for h5 files
        Kwargs:
                N/A
        Return:
                Returns a list of headers
        '''
        if not os.path.isfile(fpath):
            if debug:
                print('{} is not a valid file'.format(fpath))
            return []
        extension = os.path.splitext(fpath)[-1].strip().lower()
        if extension in ['.h5','.hdf5']:
            if not os.path.isfile(fpath.split(extension)+'.json'):
                if debug:
                    print('{} does not have a json generated'.format(fpath))
                with h5py.File(fpath,'r') as hf:
                    if grp in hf and dset in hf[grp]:
                        if isinstance(hf[grp][dset],h5py._hl.dataset.Dataset):
                            return hf[grp][dset].dtype.fields.keys()
                        elif isinstance(hf[grp][dset],h5py.Group):
                            return hf[grp][dset].keys()
                        else:
                            if debug:
                                print('The passed dataset is not a dataset or a group.  It is type {}.'.format(type(hf[grp][dset])))
                            return []
                    else:
                        if debug:
                            print('Either Group {} or Dset {} is not in file {}.'.format(grp,dset,fpath))
                        return []
            else:
                with open(fpath.split(extension)+'.json','rb') as fid:
                    dsdict = json.load(fid)
                    if grp in dsdict:
                        if dset in dsdict[grp]:
                            headers = dsdict[grp][dset]
                        else:
                            if debug:
                                print('{} not in the json file'.format(dset))
                            headers = []
                    else:
                        if debug:
                            print('{} not in the json file'.format(grp))
                        headers = []
                return headers
        elif extension in ['.pkl']:
            #TODO I'm assuming the pickled object is a dataframe
            return list(pickle.load(file(fpath,'rb')))
        elif extension in ['.csv']:
            return list(pd.read_csv(fpath))
        elif extension in ['.xlsx']:
            return list(pd.read_excel(fpath,sheet_name=dset))
        else:
            if debug:
                print('Extension {} not supported'.format(extension))
            return []

### One Offs
    def gather_files(sdir,**kwargs):
        '''
        Function searches a directory and subdirectories and returns all files.
        Input:
                sdir - the top directory to search through
        Kwargs:
                ext - A list of patterns -- ['*.txt','*h.h5']
                maxDepth - Restrict the maximum depth of directories to go down.

        Return:
                Returns a list of all the gathered files referenced from sdir
        '''
        extensions = kwargs.get('ext',['*'])
        maxDepth = kwargs.get('maxDepth',-1)
        if not isinstance(extensions,Iterable) and not isinstance(extensions,basestring):
            if debug:
                print('The ext argument you passed is not an iterable returning')
            return sdir,[]
        if not isinstance(maxDepth,int):
            if debug:
                print('the maxDepth argument you passed is not an int, going all the way down!')
            maxDepth = -1
        if maxDepth > 0:
            return sdir,[os.path.join(r,fname)[len(sdir):] for ext in extensions \
                    for r,p,f in os.walk(sdir,followlinks=False) \
                    if r[len(sdir):].count(os.sep) < maxDepth\
                    for fname in f \
                    if fnmatch.fnmatch(fname,ext)]
        elif maxDepth == 0:
            return sdir,[f for ext in extensions \
                    for f in os.listdir(sdir) \
                    if fnmatch.fnmatch(f,ext)]
        else:
            return sdir,[os.path.join(r,fname)[len(sdir):] for ext in extensions \
                for r,p,f in os.walk(sdir,followlinks=False) \
                for fname in f \
                if fnmatch.fnmatch(fname,ext)]
