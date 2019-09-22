#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 20 23:37:07 2019

@author: Jordan
"""
'''This file is a group of functions that are commonly used in Phobos'''
import os
import sys
import h5py
import pandas as pd

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
    Return:
            Returns pandas dataframe of the data from the h5 file
    '''
    data = {}
    headers = kwargs.get('headers',None)
    section = kwargs.get('section',None)
    if section:
        if len(section) < 2:
            print('The section kwarg you passed is not a correct length.')
            section = (0,200)
        elif not isinstance(section[0],int) or not isinstance(section[1],int):
            print('One or both of the indecies in the section kwarg you passed are not integers')
            section = (0,200)

    if os.path.isfile(fpath):
        with h5py.File(fpath,'r') as hf:
            if grp in hf:
                if dset in hf[grp]:
                    if headers:
                        getheaders=headers
                    else:
                        getheaders=hf[grp][dset].dtype.fields.keys()
                    if not isinstance(section,tuple):
                        data = {header:hf[grp][dset][header][...] for header in getheaders if header in hf[grp][dset].dtype.fields.keys()}
                    else:
                        data = {header:hf[grp][dset][header][section[0]:section[1]] for header in getheaders if header in hf[grp][dset].dtype.fields.keys()}
                else:
                    print('{} dataset is not in {}'.format(dset,fpath))
            else:
                print('{} group is not in {}'.format(grp,fpath))
    else:
        print('{} is not a valid file'.format(fpath))
    return pd.DataFrame(data)



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
