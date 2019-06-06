# -*- coding: utf-8 -*-
"""
Created on Mon Jun  3 17:20:39 2019

@author: Jordan
"""

import pandas as pd
import numpy as np
import re
import time
num = 10000000
trash = {'Time':np.random.randint(0,100,num),'Trash_0_This':np.random.randint(0,4,num),'Trash_1_This':np.random.randint(0,4,num),\
         'Trash_0_This_Data_1':np.random.randint(0,4,num),'Trash_1_This_Data_1':np.random.randint(0,4,num),'Trash_Covariance_1':np.random.randint(0,4,num),\
         'Bunsen_0_This':np.random.randint(0,4,num),'Bunsen_1_This':np.random.randint(0,4,num)}

y = pd.DataFrame(trash)

def containsNum(string):
    return re.search('[0-9]_',string)

def contains2Num(string):
    t = re.findall('\d+',string)
    if len(t) == 2:
        return True
    else:
        return False

def findNum(lis):
    for i,name in enumerate(lis):
        try:
            float(name)
            return i
        except:
            pass
    return -1

def buildJList(lis,index):
    z = []
    for i in range(index):
        z.append(lis[i])
    return z



commonheaders = []
sheaders = []
concatpd = {}
dictofdf = {}
for header in list(y):
    if containsNum(header):
        sheaders.append(header.split('_'))
    else:
        commonheaders.append(header)

for thing in sheaders:
    newheads = []
    index = findNum(thing)
    if index >= 0:
        key = '_'.join(buildJList(thing,index+1))
        tlkey = '_'.join(buildJList(thing,index))
        if tlkey not in dictofdf:
            dictofdf[tlkey] = {}
        if key not in dictofdf[tlkey]:
            for header in list(y):
                if key in header:
                    newheads.append(header)
            newheads.extend(commonheaders)
            dictofdf[tlkey][key] = y[newheads]
            for head in newheads:
                p = head.rsplit('_',1)[-1]
                try:
                    float(p)
                    nindex = -2
                except:
                    nindex = -1
                dictofdf[tlkey][key].rename(columns={head:head.rsplit('_',1)[nindex]},inplace=True)

for tkey in dictofdf:
    if tkey not in concatpd:
        concatpd[tkey] = pd.DataFrame()
    concatlist = []
    for lkey in dictofdf[tkey]:
        concatlist.append(dictofdf[tkey][lkey])
    concatpd[tkey] = pd.concat(concatlist,sort=False,ignore_index=True)
    
    idxlist = []
    for cpdkey in list(concatpd[tkey]):
        if cpdkey not in commonheaders:
            idxlist.append(concatpd[tkey][cpdkey].astype(str)!='nan')
    newidx = []
    for idx in idxlist:
        if len(newidx):
            newidx = newidx | idx
        else:
            newidx = idx
    concatpd[tkey] = concatpd[tkey][newidx]
                    


        