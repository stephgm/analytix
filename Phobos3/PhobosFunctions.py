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
from collections import Iterable

if True:
### Data Getting

    def get_h5_attributes(fpath,**kwargs):
        '''
        Returns a dictionary of dataframes of attributes
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
            if addDset and dset:
                for key in data:
                    data[key]['Dset'] = np.array([dset]*data[key].shape[0])
            if addGrp and grp:
                for key in data:
                    data[key]['Group'] = np.array([grp]*data[key].shape[0])
            if addFile:
                for key in data:
                    data[key]['File'] = np.array([os.path.basename(fpath)]*data[key].shape[0])
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
                thin - an integer X to gather every X'th datapoint as to thin the data
                thinpct - an integer X that will gather X% of the data
            Note:  the order of section, thin, and thinpct is as listed here
                    so if more than one of these kwargs are used, it will come
                    across and use the first of these that were implemented

        Return:
                Returns pandas dataframe of the data from the h5 file
        '''
        data = {}
        headers = kwargs.get('headers',None)
        section = kwargs.get('section',None)
        addDset = kwargs.get('addDset',False)
        thin = kwargs.get('thin',None)
        thinpct = kwargs.get('thinpct',None)
        if section:
            if isinstance(section,Iterable) and len(section) < 2:
                print('The section kwarg you passed is not a correct length.')
                section = (0,200)
            elif isinstance(section,Iterable) and (not isinstance(section[0],int) or not isinstance(section[1],int)):
                print('One or both of the indecies in the section kwarg you passed are not integers')
                section = (0,200)
            elif not isinstance(section,Iterable):
                print('The section kwarg you passed is not an iterable')
                section = (0,200)
        if thin:
            if not isinstance(thin,int):
                try:
                    print('The thin kwarg passed is not an int.  Attempting to convert')
                    thin = int(thin)
                except:
                    print('The conversion failed.  Setting thin = 5')
                    thin = 5
        if thinpct:
            if not isinstance(thinpct,int):
                try:
                    print('The thinpct kwarg passed is not an int.  Attempting to convert')
                    thinpct = int(thinpct)
                except:
                    print('The conversion failed.  Setting thinpct = 5')
                    thinpct = 5

        if os.path.isfile(fpath):
            with h5py.File(fpath,'r') as hf:
                if grp in hf:
                    if dset in hf[grp]:
                        if headers:
                            getheaders=headers
                        else:
                            getheaders=hf[grp][dset].dtype.fields.keys()
                        if isinstance(section,tuple):
                            data = {header:hf[grp][dset][header][section[0]:section[1]] for header in getheaders if header in hf[grp][dset].dtype.fields.keys()}
                        elif thin:
                            data = {header:hf[grp][dset][header][::thin] for header in getheaders if header in hf[grp][dset].dtype.fields.keys()}
                        elif thinpct:
                            size = hf[grp][dset].size
                            step = int(size/(size*thinpct*.01))
                            data = {header:hf[grp][dset][header][::step] for header in getheaders if header in hf[grp][dset].dtype.fields.keys()}
                        else:
                            data = {header:hf[grp][dset][header][...] for header in getheaders if header in hf[grp][dset].dtype.fields.keys()}

                    else:
                        print('{} dataset is not in {}'.format(dset,fpath))
                else:
                    print('{} group is not in {}'.format(grp,fpath))
        else:
            print('{} is not a valid file'.format(fpath))
        if addDset:
            data['Dset'] = np.array([dset]*len(data[data.keys()[0]]))
        return pd.DataFrame(data)

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
        extensions = kwargs.get('ext','*')
        maxDepth = kwargs.get('maxDepth',-1)
        if not isinstance(extensions,Iterable):
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
