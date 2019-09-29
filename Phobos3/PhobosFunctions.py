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

if True:
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
        Return:
                Returns the thinned array

        '''

        how = kwargs.get('how','row')
        minrows = kwargs.get('minrows',1)
        dtype = None
        seconddtype = None
        if not isinstance(array,pd.DataFrame) and not isinstance(array,np.ndarray):
            print('The data you entered was not a dataframe nor a numpy array.  Trying to convert and pass back the type you gave me. Setting how="row"')
            if isinstance(array,Iterable) and not isinstance(array,basestring):
                dtype = type(array)
                if isinstance(array,dict):
                    print('You passed in a dictionary, attempting to make it a DataFrame.  If it is nested, then your guess is as good as mine as to how it will work.  Setting how="row"')
                    try:
                        seconddtype = type(array[array.keys()[0]])
                        array = pd.DataFrame(array)
                        how = 'row'
                    except:
                        print('The conversion of the dictionary to dataframe failed. Returning input')
                        return array
                else:
                    try:
                        array = np.array(array)
                        how = 'row'
                    except:
                        print('The conversion to a numpy array was not possible! Returning input')
                        return array
            else:
                print('The array that you passed is not Iterable or it is a string, which cannot be made into a numpy array. Returning input')
                return array
        if isinstance(pct,basestring):
            try:
                pct = float(pct)
            except:
                print('Could not convert pct:{} to a float. Returning input')
                return array
        if how == 'row':
            direction = 0
        elif how == 'column':
            direction = 1
        else:
            print('How should either be "row" or "column", you entered {}.  Assuming you mean "row" because I can.'.format(how))
            direction = 0
        if not isinstance(minrows,int):
            try:
                minrows = int(minrows)
            except:
                print('Could not convert minrows kwarg to int.  Returning input')
                return array
        if pct >= 100:
            print('The percent data you are trying to get is >= 100%, returning input')
            return array
        elif pct*.01*array.shape[direction] < minrows:
            suggested = minrows*100./array.shape[direction]
            print('The percent of data you are trying to get {}%, will likely make your returned data empty. Returning {}%, this should just be 1 {}.'.format(pct,suggested,how))
            pct = suggested
        newindex = np.linspace(0,array.shape[direction]-1,int(array.shape[direction]*.01*pct),dtype=int)
        if dtype != None and isinstance(array,np.ndarray):
            array = array[newindex]
            array = dtype(array)
            return array
        elif dtype != None and isinstance(array,pd.DataFrame):
            array = array.iloc[newindex].reset_index(drop=True)
            array = array.to_dict(orient='list')
            for key in array:
                array[key] = seconddtype(array[key])
            return array
        elif isinstance(array,pd.DataFrame):
            if how == 'row':
                array = array.iloc[newindex].reset_index(drop=True)
            else:
                array = array.iloc[:,newindex].reset_index(drop=True)
            return array
        elif isinstance(array,np.ndarray):
            array = array[newindex]
            return array
        else:
            return array

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

        if os.path.isfile(fpath):
            with h5py.File(fpath,'r') as hf:
                data['file'] = pd.DataFrame({k:v for k,v in hf.attrs.iteritems()})
                if grp and grp in hf:
                    data['grp'] = pd.DataFrame({k:v for k,v in hf[grp].attrs.iteritems()})
                    if dset and dset in hf[grp]:
                        data['dset'] = pd.DataFrame({k:v for k,v in hf[grp][dset].attrs.iteritems()})
                    else:
                        print('{} is not in the h5 file {}, ommiting'.format(dset,fpath))
                else:
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
        else:
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
                gatherpct - a float X that will gather X% of the data
                Phobos - Tells function to return fpath and dataframe
            Note:  You can apply both a section and gatherpct and will work as expected

        Return:
                Returns pandas dataframe of the data from the h5 file
        '''
        data = {}
        headers = kwargs.get('headers',None)
        section = kwargs.get('section',None)
        addDset = kwargs.get('addDset',False)
        gatherpct = kwargs.get('gatherpct',None)
        Phobos = kwargs.get('Phobos',False)
        if section:
            if isinstance(section,basestring):
                print('The section kwarg you passed is a string.  Pass an iterable')
                section = (0,200)
            elif isinstance(section,Iterable) and len(section) < 2:
                print('The section kwarg you passed is not a correct length.')
                section = (0,200)
            elif isinstance(section,Iterable) and (not isinstance(section[0],int) or not isinstance(section[1],int)):
                print('One or both of the indecies in the section kwarg you passed are not integers')
                section = (0,200)
            elif not isinstance(section,Iterable):
                print('The section kwarg you passed is not an iterable')
                section = (0,200)
        if headers and not isinstance(headers,Iterable) and not isinstance(headers,basestring):
            print('The headers Kwarg you passed is not iterable.  Gathering all data')
            headers = None
        elif headers:
            if not isinstance(headers[0],basestring):
                headers = None
                print('The iteration items of the headers Kwarg are not strings. Gathering all Data')

        if not os.path.isfile(fpath):
            print('{} is not a valid file'.format(fpath))
            return pd.DataFrame()
        with h5py.File(fpath,'r') as hf:
            if grp in hf:
                if dset in hf[grp]:
                    if headers:
                        getheaders=headers
                    else:
                        getheaders=hf[grp][dset].dtype.fields.keys()
                    if isinstance(section,tuple):
                        data = {header:hf[grp][dset][header][section[0]:section[1]] for header in getheaders if header in hf[grp][dset].dtype.fields.keys()}
                    else:
                        data = {header:hf[grp][dset][header][...] for header in getheaders if header in hf[grp][dset].dtype.fields.keys()}

                else:
                    print('{} dataset is not in {}'.format(dset,fpath))
                    return pd.DataFrame()
            else:
                print('{} group is not in {}'.format(grp,fpath))
                return pd.DataFrame()

        if addDset:
            data['Dset'] = np.array([dset]*len(data[data.keys()[0]]))
        return thin_data(pd.DataFrame(data),gatherpct)

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
            print('{} is not a valid file.'.format(fpath))
            return pd.DataFrame()
        gatherpct = kwargs.get('gatherpct',100)
        headers = kwargs.get('headers',None)
        if headers and not isinstance(headers,Iterable) and not isinstance(headers,basestring):
            print('The headers Kwarg you passed is not iterable.  Gathering all data')
            headers = None
        elif headers:
            if not isinstance(headers[0],basestring):
                headers = None
                print('The iteration items of the headers Kwarg are not strings. Gathering all Data')

        y = pd.read_excel(fpath,sheet_name=sheetname)
        if headers:
            y = y[headers]

        try:
            return thin_data(y,gatherpct)
        except:
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
            print('{} is not a valid file.'.format(fpath))
            return pd.DataFrame()
        gatherpct = kwargs.get('gatherpct',100)
        headers = kwargs.get('headers',None)
        if headers and not isinstance(headers,Iterable) and not isinstance(headers,basestring):
            print('The headers Kwarg you passed is not iterable.  Gathering all data')
            headers = None
        elif headers:
            if not isinstance(headers[0],basestring):
                headers = None
                print('The iteration items of the headers Kwarg are not strings. Gathering all Data')

        y = pickle.load(file(fpath,'rb'))
        if headers:
            y=y[headers]
        try:
            return thin_data(y,gatherpct)
        except:
            print('Something went wrong while trying to thin out the data, returning un-thinned')
            return y

### Open File Attributes

    def get_groups(fpath,**kwargs):
        '''
        Function will return the groups that Phobos needs to populate GroupNameCombo
        Input:
                fpath - The full path to the file.
                        Supported Types = .h5
        Kwargs:
                useDSdict - This is for h5 files only.  Will use the dsdict to grab
                            the groups.  If a dsdict does not exist, this function
                            will create it.
        Return:
                Returns a list of group names
        '''
        if not os.path.isfile(fpath):
            print('{} is not a valid file'.format(fpath))
            return []
        extension = os.path.splitext(fpath)[1][1:].strip().lower()
        useDSdict = kwargs.get('dsdict',False)
        if extension in ['h5','hdf5']:
            if not useDSdict:
                with h5py.File(fpath,'r') as hf:
                    grps = [grp for grp in hf.keys() if isinstance(hf[grp],h5py._hl.group.Group)]
                    if grps:
                        return grps
                    else:
                        return ['/']
            else:
                print('not supported yet')
                return []
        elif extension in ['csv','xlsx','pkl']:
            print 'here'
            return ['/']
        else:
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
                useDSdict - This is for h5 files only.  Will use the dsdict to grab
                            the datasets.  If a dsdict does not exist, this function
                            will create it.  Also if commoncols are found, returns it to Phobos
        Return:
                Returns a list of datasets
        '''
        if not os.path.isfile(fpath):
            print('{} is not a valid file'.format(fpath))
            return []
        extension = os.path.splitext(fpath)[1][1:].strip().lower()
        useDSdict = kwargs.get('dsdict',False)
        if extension in ['h5','hdf5']:
            if not useDSdict:
                with h5py.File(fpath,'r') as hf:
                    if grp in hf:
                        dsets = [dset for dset in hf[grp].keys() if isinstance(hf[grp][dset],h5py._hl.dataset.Dataset)]
                        if dsets:
                            return dsets
                        else:
                            print 'returning here'
                            return []
                    else:
                        print('Group {} is not in file {}'.format(grp,fpath))
                        return []
            else:
                print('not supported yet')
                return []
        elif extension in ['csv','pkl']:
            return ['Data']
        elif extension in ['xlsx']:
            df = pd.read_excel(fpath)
            xls = pd.ExcelFile(fpath)
            return xls.sheet_names
        else:
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
                useDSdict - This is for h5 files only.  Will use the dsdict to grab
                            the datasets.  If a dsdict does not exist, this function
                            will create it.
        Return:
                Returns a list of headers
        '''
        if not os.path.isfile(fpath):
            print('{} is not a valid file'.format(fpath))
            return []
        extension = os.path.splitext(fpath)[1][1:].strip().lower()
        useDSdict = kwargs.get('dsdict',False)
        if extension in ['h5','hdf5']:
            if not useDSdict:
                with h5py.File(fpath,'r') as hf:
                    if grp in hf and dset in hf[grp].keys():
                        if isinstance(hf[grp][dset],h5py._hl.dataset.Dataset):
                            return hf[grp][dset].dtype.fields.keys()
                        else:
                            print('The passed dataset is not a dataset.  It is type {}.'.format(type(hf[grp][dset])))
                            return []
                    else:
                        print('Either Group {} or Dset {} is not in file {}.'.format(grp,dset,fpath))
                        return []
            else:
                print('not supported yet')
                return []
        elif extension in ['pkl']:
            #TODO I'm assuming the pickled object is a dataframe
            return list(pickle.load(file(fpath,'rb')))
        elif extension in ['csv']:
            return list(pd.read_csv(fpath))
        elif extension in ['xlsx']:
            return list(pd.read_excel(fpath,sheet_name=dset))
        else:
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
            print('The ext argument you passed is not an iterable returning')
            return sdir,[]
        if not isinstance(maxDepth,int):
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
