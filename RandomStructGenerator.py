#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 19 18:54:57 2019

@author: FCL
"""

import numpy as np
import pandas as pd
def makeDictArray(**kwargs):
    data = {}
    size = kwargs.get('size',20)
    strings = 'What is this sentence about? And why do you care?'.split(' ')
    bools = [True,False]
    bytestrings = list(map(lambda x:bytes(x,encoding='utf-8'),strings))
    data['ByteString'] = np.random.choice(bytestrings, size)
    data['Unicode'] = np.random.choice(strings, size)
    data['Integer'] = np.random.randint(0,100,size)
    data['Float'] = np.random.random(size)
    data['Bool'] = np.random.choice(bools,size)
    
    return data

def makeDF(**kwargs):
    size = kwargs.get('size',20)
    data = makeDictArray(size=size)
    return pd.DataFrame(data)

def makeStructArray(**kwargs):
    size = kwargs.get('size',20)
    data = makeDictArray(size=size)
    bullshit = np.zeros(size, dtype={'names':[key for key in data],
                          'formats':[data[key].dtype for key in data]})
    for key in data:
        bullshit[key] = data[key]
    return bullshit
    
x = makeDF()
y = makeDictArray()
z = makeStructArray()

