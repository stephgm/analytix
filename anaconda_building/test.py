#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  4 14:37:51 2018

@author: localadmin
"""
try:
    from mpl_toolkits.basemap import Basemap
except:
    print('No Basemap')
import cartopy
#import gi
import pandas
import shapely
# need this for reduced
import pptx
import numpy
import numba
import zmq
import scipy
import actdiag, blockdiag, nwdiag, seqdiag, arrow, colorcet, dill, pathlib, seaborn
#import scandir
print('numpy   : '+numpy.__version__)
print('numba   : '+numba.__version__)
print('scipy   : '+scipy.__version__)
print('pandas  : '+pandas.__version__)
print('cartopy : '+cartopy.__version__)
import h5py
print('h5py    : '+h5py.__version__)
dtb = numpy.dtype([('this','f8'),('that','O')])
def convert2SpecialDtype(idt):
    ndtl = []
    for dname,desc in idt.descr:
        if desc[1] == 'S' or desc[1] == 'O' or desc[1] == 'U':
            ndtl.append((dname,h5py.special_dtype(vlen=str)))
        else:
            ndtl.append((dname,desc))
    return numpy.dtype(ndtl)
dta = convert2SpecialDtype(dtb)
#import plotnine
print('dont forget shutil os.chmod and sphinx')
