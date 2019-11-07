#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 28 05:04:34 2018

@author: hollidayh
"""
nr=1000000
nr=100
no2=int(nr/2)
no4=int(nr/4)
import sys
import os
import numpy
import h5py
import pandas
sys.path.append(os.path.dirname(__file__))
from Phobos3 import PhobosFunctions as PF
DT = h5py.special_dtype(vlen=str)
def writeDataframe2File(infile,grpStr,df,**kwargs):
    force = kwargs.get('force',False)
    if os.path.isfile(infile):
        mode = 'a'
    else:
        mode = 'w'
    try:
        hh = h5py.File(infile,mode)
    except:
        print('Error opening : {}'.format(infile))
        return
    if grpStr in hh and force:
        del(hh[grpStr])
    g = hh.create_group(grpStr,track_order=True)
    for key in list(df):
        if df[key].dtype.kind == 'O':
            g.create_dataset(name = key, data = df[key], dtype = DT)
            #g.create_dataset(name = key, data = numpy.array(df[key],dtype='S'))
        else:
            g.create_dataset(name = key, data = df[key])
    hh.close()
    
df = pandas.DataFrame()
df['sensorName'] = numpy.array(['']*nr)
protarr = numpy.array(['F-SERIES']*no2+['B-SERIES']*no2)
numpy.random.shuffle(protarr)
idx = protarr == 'F-SERIES'
df.loc[idx,'sensorName']  = 'THAAD'
df.loc[~idx,'sensorName'] = 'TPY-2'
df['protocol'] = protarr.copy()
df['timeRvInTrack']   = numpy.random.rand(nr) * 1000.
df['timeTankInTrack'] = numpy.random.rand(nr) * 1000.
writeDataframe2File('idap.h5','/data',df,force=True)
#ndf = PF.get_h5_data('idap.h5','/','data')
sys.exit(0)
hh = h5py.File('idap.h5','w')
grp = hh.create_group('/data')
grp.create_dataset(name = 'protocol', data = df['protocol'], dtype=DT)
hh.close()
### original stuff
hh = h5py.File('idap.h5','w')
protarr = numpy.array(['F-SERIES']*no2+['B-SERIES']*no2)
numpy.random.shuffle(protarr)
sensorarr = numpy.array(['']*nr,dtype='S30')
idx = protarr == 'F-SERIES'
sensorarr[idx]  = 'THAAD'
sensorarr[~idx] = 'TPY-2'
dt = numpy.dtype([('sensorName','S30'),
                  ('protocol','S30'),
                  ('timeRvTrack','f8'),
                  ('timeTankTrack','f8'),
                  ('inSearchPlan','u2')])
hh.create_dataset(name = 'ota.acquisitionSummary',
                  data =
                  numpy.array(
                  zip(sensorarr,
                      protarr,
                      numpy.random.rand(nr) * 1000.,
                      numpy.random.rand(nr) * 1000.,
                      numpy.round(numpy.random.rand(nr)).astype('u2')),
                 dtype=dt))
dt = numpy.dtype([('sensorName','S30'),
                  ('decision','S30'),
                  ('confidence','f8'),
                  ('timeRvCall','f8'),
                  ('timeTankCall','f8'),
                  ('isTrueLethal','u2')])
dArray = numpy.array('RV TANK JUNK NO_STATEMENT'.split() * no4)
numpy.random.shuffle(dArray)
hh.create_dataset(name = 'ota.discrimSummary',
    data = numpy.array(
            zip(sensorarr,dArray,numpy.random.rand(nr) * 100.,
                numpy.random.rand(nr) * 1000.,
                numpy.random.rand(nr) * 1000.,
                numpy.round(numpy.random.rand(nr)).astype('u2')),
            dtype = dt))
hh.close()