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
print('numpy  : '+numpy.__version__)
print('scipy  : '+scipy.__version__)
print('pandas : '+pandas.__version__)
print('cartopy : '+cartopy.__version__)
#import plotnine
