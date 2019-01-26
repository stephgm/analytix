#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 28 05:04:34 2018

@author: hollidayh
"""
nr=1000000
no2=nr/2
no4=nr/4
import numpy
import h5py
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