#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar  7 23:51:10 2020

@author: marlowcj
"""
import os
import sys
import numpy as np

if not hasattr(sys, 'frozen'):
    RELATIVE_LIB_PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    if __name__ == '__main__':
        sys.path.append(RELATIVE_LIB_PATH)
        sys.path.pop(0)
else:
    RELATIVE_LIB_PATH = os.path.dirname(sys.executable)


lengths = {'m':1,'mi':1609.34,'NM':1852}
times = {'s':1,'hr':3600,'min':60}
prefixes = {'n':1e-9,'u':1e-6,'m':1e-3,'':1,'k':1e3,'M':1e6,'G':1e9}

conversionDict = {f'{k}{v}':prefixes[k]*lengths[v] for k in prefixes for v in lengths}
conversionDict.update({f'{k}{v}':prefixes[k]*times[v] for k in prefixes for v in times})

UnitAliases = {'Distance':{'m':['meter','Meter','METER','meters','Meters','METERS','m','M'],
               'mi':['mile','Mile','MILE','miles','Miles','MILES','mi','Mi','MI'],
               'NM':['nauticalmile','nautilcalMile','NauticalMile','NAUTICALMILE',
                     'nauticalmiles','nauticalMiles','NauticalMiles','NAUTICALMILES',
                     'NM','nM','nm']},
               'Time':{'s':['second','seconds','Second','SECOND','Seconds','SECONDS','s','S'],
               'hr':['hour','Hour','HOUR','hours','Hours','HOURS','hr','HR','Hr','hrs','HRS','Hrs'],
               'min':['minute','Minute','MINUTE','minutes','Minutes','MINUTES','min','Min','MIN',
                      'mins','Mins','MINS']}}
PrefixAliases = {'n':['nano','Nano','NANO','n'],
                 'u':['micro','Micro','MICRO','u'],
                 'm':['mili','Mili','MILI','milli','Milli','MILLI','m'],
                 '': [''],
                 'k':['kilo','Kilo','KILO','k'],
                 'M':['mega','Mega','MEGA','M'],
                 'G':['giga','Giga','GIGA','G']}

radianalias = ['radian','r','rad','radians']

def convertUnit(value,iUnit,oUnit,ctype='Distance'):
    iPrefixkey = None
    iUnitkey = None
    oPrefixkey = None
    oUnitkey = None
    if ctype not in UnitAliases:
        return np.nan
    
    if len(iUnit) == 1:
        #Assuming this is just a unit with no prefix
        iPrefixkey = ''
        iUnitkey = iUnit
    else:
        #Just quickly check to see if the iUnit is an alias for a unit
        #There should not be any mix up
        for ua in UnitAliases[ctype]:
            if iUnit == UnitAliases[ctype][ua]:
                iUnitkey = iUnit
                iPrefixkey = ''
                break
    if len(oUnit) == 1:
        #Assuming this is just a unit
        oPrefixkey = ''
        oUnitkey = oUnit
    else:
        #Just quickly check to see if the oUnit is an alias for a unit
        for ua in UnitAliases[ctype]:
            if oUnit == UnitAliases[ctype][ua]:
                oUnitkey = oUnit
                oPrefixkey = ''
    if not iPrefixkey:
        #Failed the previous tests... gotta do some more checking
        for key in PrefixAliases:
            for alias in PrefixAliases[key]:
                if iUnit.startswith(alias):
                    la = len(alias)
                    for ukey in UnitAliases[ctype]:
                        for ualias in UnitAliases[ctype][ukey]:
                            if iUnit[la:] == ualias:
                                iPrefixkey = key
                                iUnitkey = ukey
                                break
                        if iUnitkey and iPrefixkey:
                            break
                if iUnitkey and iPrefixkey:
                    break
            if iUnitkey and iPrefixkey:
                break
    if not oPrefixkey:
        for key in PrefixAliases:
            for alias in PrefixAliases[key]:
                if oUnit.startswith(alias):
                    la = len(alias)
                    for ukey in UnitAliases[ctype]:
                        for ualias in UnitAliases[ctype][ukey]:
                            if oUnit[la:] == ualias:
                                oPrefixkey = key
                                oUnitkey = ukey
                                break
                        if oUnitkey and oPrefixkey:
                            break
                if oUnitkey and oPrefixkey:
                    break
            if oUnitkey and oPrefixkey:
                break 
    if not oUnitkey or not iUnitkey:
        return np.nan
    return value*conversionDict[f'{iPrefixkey}{iUnitkey}']/conversionDict[f'{oPrefixkey}{oUnitkey}']
