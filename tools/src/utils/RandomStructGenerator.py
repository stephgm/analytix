#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 19 18:54:57 2019

@author: FCL
"""
import sys
import os
import numpy as np
import pandas as pd
def makeDictArray(**kwargs):
    data = {}
    size = kwargs.get('size',20)
    haveNulls = kwargs.get('nulls',False)
    strings = 'What is this sentence about? And why do you care?'.split(' ')
    bools = [True,False]
    if haveNulls:
        nums = [1.,2.,np.nan,pd.NA]
    else:
        nums = [1.,2.,np.nan]
    bytestrings = list(map(lambda x:bytes(x,encoding='utf-8'),strings))
    data['ByteString'] = np.random.choice(bytestrings, size)
    data['Unicode'] = np.random.choice(strings, size)
    data['Integer'] = np.random.randint(0,10,size)
    data['Float'] = np.random.random(size)
    data['Bool'] = np.random.choice(bools,size)
    if haveNulls:
        data['Time'] = np.random.choice([100.,101.,102.,pd.NA],size)
    else:
        data['Time'] = np.random.choice([100.,101.,102.],size)
    data['NanIsh'] = np.random.choice(nums,size)
    return data

def makeDF(**kwargs):
    return pd.DataFrame(makeDictArray(**kwargs))

def makeStructArray(**kwargs):
    size = kwargs.get('size',20)
    data = makeDictArray(size=size)
    z = np.zeros(size, dtype={'names':[key for key in data],
                          'formats':[data[key].dtype for key in data]})
    for key in data:
        z[key] = data[key]
    return z

if __name__ == '__main__':

    x = makeDF()
    sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
    import utils.StructureUtils as sutil
    xx = sutil.FilterOnField(x,'NanIsh','==',1.)
    xx = sutil.FilterOnField(x,'NanIsh','==',[1,2])
    # y = makeDictArray()
    # z = makeStructArray()

    # xx = {}
    # for uid in pd.unique(x['Integer']):
    #     idx = x['Integer'] == uid
    #     xx[uid] = pd.DataFrame({'Time':x.loc[idx,'Time'],
    #                             # 'Integer':x.loc[idx,'Integer'],
    #                             f'Float_{uid}':x.loc[idx,'Float']})
    #     xx[uid].sort_values('Time',inplace=True)

    # if len(xx) > 1:
    #     keys = list(xx)
    #     z = pd.merge(xx[keys[0]],xx[keys[1]],
    #                  how='left',on='Time')
    #     z.fillna(value=0.,inplace=True)
    #     for i in range(2,len(keys)):
    #         z = pd.merge(z,xx[keys[i]],how='left',on='Time')
    #                      # suffixes=('',f'_{keys[i]}'))
    #         z.fillna(value=0.,inplace=True)
    #     keys = [key for key in z if key.startswith('Float_')]
    #     z['sum'] = z[keys].apply(lambda x: sum(x), axis=1)
    #     # z.drop(columns=keys,inplace=True)
