#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 16 20:20:13 2018

@author: hollidayh
"""

import numpy
import h5py

dt = numpy.dtype([('time','f8'),('pos','f8'),('vel','f8')])

data = numpy.array([(a,b,c) \
                    for a,b,c in zip(numpy.arange(4),\
                                     numpy.arange(4)+1,\
                                     numpy.arange(4)*4)],dtype=dt)

hh = h5py.File('bigdata.h5','w')
for fld in 'time pos vel'.split():
    hh.create_dataset(name = fld, data = numpy.random.rand(10000))
hh.close()

hh = h5py.File('example.h5','w')
hh.create_dataset(name = 'data1', data = data)
grp = hh.create_group('/data_group')
for i,name in enumerate(('time','pos','vel')):
    grp.create_dataset(name = name, data = numpy.arange(4.)+2*i)
grp = hh.create_group('/data_group_links')
for i,name in enumerate(('time','pos','vel')):
    #hh['data_group_links'][name] = h5py.SoftLink('/data_group/'+name)
    # does not work in data sets
    #hh['data_group_links'][name] = h5py.SoftLink('/data1/'+name)
    hh['data_group_links'][name] = h5py.ExternalLink('bigdata.h5','/'+name)
hh.close()

with h5py.File('example.h5','r') as hh:
    x = hh['data_group_links']['time'][...]
print(x)