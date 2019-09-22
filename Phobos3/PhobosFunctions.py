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

def get_h5_data(fpath,group,dset,**kwargs):
    '''
    Given a filepath, group, and dataset for an h5 file, this function
    returns the data in a pandas dataframe
    Input:
            fpath - the file path to the h5 file
            group - the group in the h5 file
            dset - the dataset inside the group of the h5 file
    Kwargs:
            headers - a list of headers to extract from the h5 dataset
            maxrows - integer indicating max number or rows to return = [:maxrows]

    Return:
            Returns pandas dataframe of the data from the h5 file
    '''
    data = {}
    headers = kwargs.get('headers',None)
    maxrows = kwargs.get('maxrows',None)
    if os.path.isfile(fpath):
        with h5py.File(fpath,'r') as hf:
            if group in hf:
                if dset in hf[group]:
                    if headers:
                        getheaders=headers
                    else:
                        getheaders=hf[grp][dset].dtype.fields.keys()
                    if not isinstance(maxrows,int):
                        data = {header:hf[grp][dset][header][...] for header in getheaders if header in hf[grp][dset].keys()}
                    else:
                        data = {header:hf[grp][dset][header][:maxrows] for header in getheaders if header in hf[grp][dset].keys()}
                else:
                    print('{} dataset is not in {}'.format(dset,fpath))
            else:
                print('{} group is not in {}'.format(grp,fpath))
    else:
        print('{} is not a valid file'.format(fpath))
    return pd.DataFrame(data)



def get_groups(fpath,**kwargs):
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
