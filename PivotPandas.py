#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 23 20:33:45 2019

@author: Jordan
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from six import string_types
import os

tracked = [0,1]
engaged = [0,1]
ner = ['NEE','Out of Inventory','Manual NE','Missed']
region = ['USA','Japan','Guam','Hawaii']
sensor = ['Tpy2','THAAD','Aegis']

numpoints = 10000

this = {'Tracked':np.random.choice(tracked, numpoints, p=[0.5, 0.5]),
        'Engaged':np.random.choice(engaged,numpoints,p=[.5,.5]),
        'Non_Eng_Reason':np.random.choice(ner, numpoints, p=[0.25,0.25,.25,.25]),
        'Region':np.random.choice(region, numpoints, p=[0.25,.25,.25,.25]),
        'Sensor':np.random.choice(sensor, numpoints, p=[0.33, 0.34,.33])}

y = pd.DataFrame(this)
def PivotTotals(iDF,columnField,SplitoutFields,**kwargs):
    if not isinstance(iDF,pd.DataFrame):
        return
    if isinstance(columnField,string_types):
        columnField = [columnField]
    if len(columnField) != 1:
        print('columnField should be a string or list of 1 string')
        return
    if not set(columnField).issubset(set(iDF)):
        print('{} is not in the dataframe'.format(columnField[0]))
        return
    if not set(SplitoutFields).issubset(set(iDF)):
        print('SplitoutFields {} not in the dataframe'.format(repr(SplitoutFields)))
        return
    allfields = SplitoutFields+columnField
    iDF = iDF[allfields]
    columnField = columnField[0]
    iDF = iDF.pivot_table(values=columnField,index=SplitoutFields,columns=columnField,
                          aggfunc=lambda x: '({}/{}) {}%'.format(x.shape[0],
                                             iDF[iDF[columnField]==x[columnField].iloc[0]].shape[0],
                                             round(float(x.shape[0])/iDF[iDF[columnField]==x[columnField].iloc[0]].shape[0],3)*100))
    return iDF

xx = PivotTotals(y,'Non_Eng_Reason',['Sensor','Region'])
#Export to excel
filename = os.path.join(os.path.expanduser('~'),'Desktop','pivotExample.xlsx')
xx.to_excel(filename)
