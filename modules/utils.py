#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  1 05:04:40 2018

@author: hollidayh
"""
import os
import time
from io import StringIO
import numpy
import csv
def thisAnalysis(epath,**kwargs):
    print('here')
    print(epath)
    newvar = kwargs.pop('force',True)
    print(newvar)
    if newvar:
        a
    time.sleep(1)
    print('waking')

def csvWriter(x,outfile):
    if isinstance(x,numpy.ndarray):
        if not x.size:
            return
        hdr = x.dtype.names
    elif isinstance(x,dict):
        if not x:
            return
        hdr = list(x.keys())
    xs = {fld:x[fld].astype('U') for fld in hdr}
    out = StringIO()
    out.write(','.join(hdr)+'\n')
    for i in range(xs[hdr[0]].size):
        for fld in hdr[:-1]:
            out.write(xs[fld][i]+',')
        out.write(xs[hdr[-1]][i]+'\n')
    out.flush()
    with open(outfile,'w') as fid:
        fid.write(out.getvalue())
    out.close()

def csvReaderLargeAdar(filename,headerList=[]):
    data = {}
    with open(filename, "r") as csvfile:
        datareader = csv.reader(csvfile)
        count = 0
        # skip the first empty line
        next(datareader)
        # and the header line
        hdrs = next(datareader)
        # and another empty line
        next(datareader)
        # only get the headers we care about if entered
        if headerList:
            hdrIdx = []
            for hdr in headerList:
                if hdr in hdrs:
                    hdrIdx.append(hdrs.index(hdr))
        else:
            hdrIdx = list(range(len(hdrs)))
        data = {hdrs[i]:[] for i in hdrIdx}
        add = {hdr:data[hdr].append for hdr in data}
        for row in datareader:
            for i in hdrIdx:
                add[hdrs[i]](row[i])
    x = {}
    if data:
        for fld in list(data.keys()):
            try:
                x[fld] = numpy.asfarray(data[fld])
            except:
                x[fld] = numpy.array(data[fld],dtype='U')
            del(data[fld])
    return x

def read_ini(infile):
    if not os.path.isfile(infile):
        return {}
    x = {}
    with open(infile,'r') as fid:
        lines = fid.read().splitlines()
    topic = ''
    field = ''
    for line in lines:
        if line.startswith('[') and line.endswith(']'):
            topic = line[1:-1]
            if topic not in x:
                x[topic] = {}
            continue
        if not topic:
            continue
        if line.count('=') == 1:
            fld,dta = line.split('=')
            if fld not in x[topic]:
                x[topic][fld] = []
            x[topic][fld].extend(dta.split(','))
    for topic in x:
        for fld in x[topic]:
            x[topic][fld] = sorted(set(x[topic][fld]))
    return x

def write_ini(x,ofile):
    out = StringIO()
    for topic in x:
        out.write('['+str(topic)+']\n')
        for fld in x[topic]:
            out.write(str(fld)+'='+','.join(map(str,x[topic][fld]))+'\n')
    out.flush()
    with open(ofile,'w') as fid:
        fid.write(out.getvalue())
    out.close()