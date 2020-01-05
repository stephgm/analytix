#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan  4 10:24:57 2020

@author: klinetry
"""


import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from six import string_types
import os
import copy
import matplotlib.pyplot as plt
import seaborn as sns

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

def summary_by_column(df,odf,columnField):
    odf = copy.deepcopy(odf)
    for field in df:
        if field not in [columnField]:
            odf = odf[odf[field]==df[field].iloc[0]]
    x = df.shape[0]
    y = odf.shape[0]
    pct = np.round(100*x/y,2)
    return f'({x}/{y}) {pct}%'

def summary_by_row(df,odf,columnField):
    odf = copy.deepcopy(odf)
    odf = odf[odf[columnField]==df[columnField].iloc[0]]
    x = df.shape[0]
    y = odf.shape[0]
    pct = np.round(100*x/y,2)
    return f'({x}/{y}) {pct}%'

def make_heatmap_from_df(df,xheader,yheader,cbarori=[],fmt=''):
    if not isinstance(df,pd.DataFrame):
        return
    fig, ax = plt.subplots()
    
    if isinstance(df.index,(list,tuple)):
        how = 1
    else:
        how = 0
    if fmt:
        nloc = fmt.find('n')
        dloc = fmt.find('d')
        nb,ne,db,de = -1,-1,-1,-1
        if nloc > 0 and dloc > 1 and dloc < len(fmt):
            nb = fmt[nloc-1]
            ne = fmt[nloc+1]
            db = fmt[dloc-1]
            de = fmt[dloc+1]
            def formatIt(nb,ne,db,de,series):
                nseries = series.str.split(nb).str[1]
                nseries = nseries.str.split(ne).str[0]
                dseries = series.str.split(db).str[1]
                dseries = dseries.str.split(de).str[0]
                return nseries.astype(float)/dseries.astype(float)
        elif nloc == 0 and dloc > 1 and dloc < len(fmt):
            ne = fmt[1]
            db = fmt[dloc-1]
            de = fmt[dloc+1]
            def formatIt(nb,ne,db,de,series):
                nseries = series.str.split(ne).str[0]
                dseries = series.str.split(db).str[1]
                dseries = dseries.str.split(de).str[0]
                return nseries.astype(float)/dseries.astype(float)
        elif nloc > 0 and dloc == len(fmt):
            nb = fmt[nloc-1]
            ne = fmt[nloc+1]
            db = fmt[dloc-1]
            def formatIt(nb,ne,db,de,series):
                nseries = series.str.split(nb).str[1]
                nseries = nseries.str.split(ne).str[0]
                dseries = series.str.split(db).str[1]
                return nseries.astype(float)/dseries.astype(float) 
        elif nloc == 0 and dloc == len(fmt):
            ne = fmt[1]
            db = fmt[dloc-1]
            def formatIt(nb,ne,db,de,series):
                nseries = series.str.split(ne).str[0]
                dseries = series.str.split(db).str[1]
                return nseries.astype(float)/dseries.astype(float) 
        elif nloc > 0 and dloc < 0:
            nb = fmt[nloc-1]
            ne = fmt[nloc+1]
            def formatIt(ne,nb,db,de,series):
                nseries = series.str.split(nb).str[1]
                nseries = nseries.str.split(ne).str[0]
                return nseries.astype(float)
        elif nloc == 0 and dloc < 0:
            ne = fmt[1]
            def formatIt(nb,ne,db,de,series):
                nseries = series.str.split(ne).str[0]
                return nseries.astype(float)
                
        numericdf = df.apply(lambda x:formatIt(nb,ne,db,de,x))
        im = ax.imshow(numericdf)
    else:
        im = ax.imshow(df)
    
    if how:
        ax.set_xticklabels(list(df))
        ax.set_yticklabels([f'{y[0]}-{y[1]}' for y in df.index])
    else:
        ax.set_xticklabels(list(df))
        ax.set_yticklabels([f'{y}' for y in df.index])
    

y = pd.DataFrame(this)
def PivotTotals(iDF,columnField,SplitoutFields,**kwargs):
    how = kwargs.get('how',1)
    if how in [1,'column','horizontal']:
        how = 1
    else:
        how = 0
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
    if how == 0:
        iDF = iDF.pivot_table(values=columnField,index=SplitoutFields,columns=columnField,
                              aggfunc=lambda x: summary_by_row(x, iDF, columnField))
    else:
        iDF = iDF.pivot_table(values = columnField,index=SplitoutFields,columns=columnField,
                            aggfunc=lambda x: summary_by_column(x, iDF, columnField))
    return iDF

xx = PivotTotals(y,'Non_Eng_Reason',['Sensor','Region'])
yy = PivotTotals(y, 'Non_Eng_Reason', ['Sensor','Region'], how = 1)

# make_heatmap_from_df(xx,'Region','Sensor',fmt='(n/d)')


