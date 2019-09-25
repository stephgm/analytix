#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Aug  9 20:45:15 2019

@author: Jordan
"""

import pandas as pd

orkeys = [str(i) for i in range(10)]
orkeys.insert(0,'')

def handleValue(df,header,value):
        if header in df:
            dtype = df[header].dtype.kind
            if dtype in ['u','i']:
                try:
                    value = int(value)
                except:
                    return None
            elif dtype in ['b']:
                try:
                    value = value == 'True'
                except:
                    return None
            elif dtype in ['f']:
                try:
                    value = float(value)
                except:
                    return None
        return value

def generalFilter(df,procedures,**kwargs):
    '''
    Function returns a filtered dataframe!
    Input:
            df - dataframe that needs to be sorted
            procedures - a list of lists of commands to do (may change this later)
                        [['header','Greater Than','value','OrKey','AndKey']]
    Kwargs:
            reset - Bool to reset index or not
    Return:
            Returns the filtered dataframe
    '''
    if not isinstance(df,pd.DataFrame):
        print('The data passed is not a dataframe, returning what you gave me')
        return df
    if not isinstance(procedures,list):
        print('The procedures passed were not a list, returning the original dataframe')
        return df

    reset = kwargs.get('reset',True)
    if not isinstance(reset,bool):
        print('The reset kwarg passed is not True or False, setting to True')
        reset = True

    sorting = False
    orchecks = False
    OrFilt = False
    AndFilt = False
    sort = False
    sortType = []
    sortHeader = []
    andchecks = False
    andcheckdict = dict((akey,dict((okey,[])for okey in orkeys)) for akey in orkeys)
    orcheckdict = dict((key,[]) for key in orkeys)
    for header,sortby,value,orcheck,andcheck in procedures:
        if header not in df:
            print('Skipping filter containing "{}", because it is not in a column name'.format(header))
            continue
        orchecks = False
        andchecks = False
        dtype = df[header].dtype.kind
        if sortby.lower() in ['less than','lessthan','<','lt']:
            sortby = 'Less Than'
        elif sortby.lower() in ['greater than','greaterthan','>','gt']:
            sortby = 'Greater Than'
        elif sortby.lower() in ['equalto','equal to','equal','equals','=','==','eq','et','e']:
            sortby = 'Equal To'
        elif sortby.lower() in ['not equal to','not equal','!equal','!=','~=','ne','net','not','<>']:
            sortby = 'Not Equal To'
        elif sortby.lower() in ['in range','between','range','in between','betwixt']:
            sortby = 'In Range'
        elif sortby.lower() in ['not in range','not between','!range','not in between','not betwixt']:
            sortby = 'Not In Range'
        if sortby not in ['Less Than','Greater Than','Equal To','Not Equal To',
                          'In Range','Not In Range','Starts With','Does Not Start With',
                          'Ends With','Does Not End With','Contains','Does Not Contain',
                          'Ascending Order','Descending Order']:
            print('Skipping the filter containing operand "{}", because it is invalid'.format(sortby))
            continue

        if 'Range' in sortby:
            if ':' not in value:
                print('Skipping the filter "{} {}", because there is no ":" between values'.format(header,sortby))
                continue
            valueLower,valueUpper = value.split(':')
            if dtype == 'b':
                lowerValue = lowerValue == 'True'
                upperValue = upperValue == 'True'
            elif dtype != 'O':
                if not valueLower:
                    valueLower = -np.inf
                else:
                    try:
                        valueLower = float(valueLower)
                    except:
                        print('Skipping the filter "{} {}" because "{}" cannot be made a number'.format(header,sortby,header))
                        continue
                if not valueUpper:
                    valueUpper = np.inf
                else:
                    try:
                        valueUpper = float(valueUpper)
                    except:
                        print('Skipping the filter "{} {}" because "{}" cannot be made a number'.format(header,sortby,value))
                        continue
        elif 'Range' in sortby and not value.isalnum() and 'Order' not in sortby:
            print ('Skipping the filter "{} {}" because "{}" contains special characters'.format(header,sortby,value))
            continue
        elif 'Order' not in sortby:
            value = handleValue(df,header,value)
            if value == None:
                print ('Skipping the filter "{} {}" because "{}" cannot be made type {}'.format(header,sortby,value,dtype))
                continue
                #if 'With' in sortby and dtype not in ['O','b']:
                #Dont think i need this, but its here if i do
#                else:
#                    if 'With' in sortby:
#                        try:
#                            value = int(value)
#                        except:
#                            print( value + ' cannot be of type int')
#                    else:
#                        try:
#                            value = float(value)
#                        except:
#                            print( value + ' cannot be of type float')
#                            continue
        if orcheck:
            or_grouping = True
            OrFilt = True
        if andcheck:
            and_or_grouping = True
            or_grouping = True
            AndFilt = True
            OrFilt = True
        if sortby == 'Less Than':
            if orchecks and not andchecks:
                orcheckdict[orcheck].append(df[header]<value)
            elif orchecks and andchecks:
                andcheckdict[orcheck][andcheck].append(df[header]<value)
            else:
                df = df[df[header]<value]
        if sortby == 'Greater Than':
            if orchecks and not andchecks:
                orcheckdict[orcheck].append(df[header]>value)
            elif orchecks and andchecks:
                andcheckdict[orcheck][andcheck].append(df[header]>value)
            else:
                df = df[df[header]>value]
        if sortby == 'Equal To':
            if orchecks and not andchecks:
                orcheckdict[orcheck].append(df[header]==value)
            elif orchecks and andchecks:
                andcheckdict[orcheck][andcheck].append(df[header]==value)
            else:
                df = df[df[header]==value]
        if sortby == 'Not Equal To':
            if orchecks and not andchecks:
                orcheckdict[orcheck].append(df[header]!=value)
            elif orchecks and andchecks:
                andcheckdict[orcheck][andcheck].append(df[header]!=value)
            else:
                df = df[df[header]!=value]
        if sortby == 'In Range':
            if orchecks and not andchecks:
                orcheckdict[orcheck].append(df[header].between(valueLower,valueUpper))
            elif orchecks and andchecks:
                andcheckdict[orcheck][andcheck].append(df[header].between(valueLower,valueUpper))
            else:
                df = df[df[header].between(valueLower,valueUpper)]
        if sortby == 'Not In Range':
            if orchecks and not andchecks:
                orcheckdict[orcheck].append(~df[header].between(valueLower,valueUpper))
            elif orchecks and andchecks:
                andcheckdict[orcheck][andcheck].append(~df[header].between(valueLower,valueUpper))
            else:
                df = df[~df[header].between(valueLower,valueUpper)]
        if sortby == 'Starts With':
            if orchecks and not andchecks:
                orcheckdict[orcheck].append(df[header].astype(str).str.lower().str.startswith(str(value)))
            elif orchecks and andchecks:
                andcheckdict[orcheck][andcheck].append(df[header].astype(str).str.lower().str.startswith(str(value)))
            else:
                df = df[df[header].astype(str).str.lower().str.startswith(str(value))]
        if sortby == 'Does Not Start With':
            if orchecks and not andchecks:
                orcheckdict[orcheck].append(~df[header].astype(str).str.lower().str.startswith(str(value)))
            elif orchecks and andchecks:
                andcheckdict[orcheck][andcheck].append(~df[header].astype(str).str.lower().str.startswith(str(value)))
            else:
                df = df[~df[header].astype(str).str.lower().str.startswith(str(value))]
        if sortby == 'Ends With':
            if orchecks and not andchecks:
                orcheckdict[orcheck].append(df[header].astype(str).str.lower().str.endswith(str(value)))
            elif orchecks and andchecks:
                andcheckdict[orcheck][andcheck].append(df[header].astype(str).str.lower().str.endswith(str(value)))
            else:
                df = df[df[header].astype(str).str.lower().str.endswith(str(value))]
        if sortby == 'Does Not End With':
            if orchecks and not andchecks:
                orcheckdict[orcheck].append(~df[header].astype(str).str.lower().str.endswith(str(value)))
            elif orchecks and andchecks:
                andcheckdict[orcheck][andcheck].append(~df[header].astype(str).str.lower().str.endswith(str(value)))
            else:
                df = df[~df[header].astype(str).str.lower().str.endswith(str(value))]
        if sortby == 'Contains':
            if orchecks and not andchecks:
                orcheckdict[orcheck].append(df[header].astype(str).str.lower().str.contains(str(value),case=False))
            elif orchecks and andchecks:
                andcheckdict[orcheck][andcheck].append(df[header].astype(str).str.lower().str.contains(str(value),case=False))
            else:
                df = df[df[header].astype(str).str.lower().str.contains(str(value),case=False)]
        if sortby == 'Does Not Contain':
            if orchecks and not andchecks:
                orcheckdict[orcheck].append(~df[header].astype(str).str.lower().str.contains(str(value),case=False))
            elif orchecks and andchecks:
                andcheckdict[orcheck][andcheck].append(~df[header].astype(str).str.lower().str.contains(str(value),case=False))
            else:
                df = df[~df[header].astype(str).str.lower().str.contains(str(value),case=False)]
        if sortby == 'Ascending Order':
            sort = True
            sortType.append(True)
            sortHeader.append(header)
        if sortby == 'Descending Order':
            sort = True
            sortType.append(False)
            sortHeader.append(header)
    if OrFilt and AndFilt:
        oidxs = []
        for okey in andcheckdict:
            idxs = []
            for akey in andcheckdict[okey]:
                if andcheckdict[okey][akey]:
                    idxs.append(pd.Series(np.array([True]*df.shape[0])))
                    for idxa in andcheckdict[okey][akey]:
                        idxs[-1] = idxs[-1] & idxa
                    orcheckdict[okey].append(idxs[-1])
        AndFilt = False


    if OrFilt and not AndFilt:
        idxs = pd.Series(np.array([True]*df.shape[0]))
        for key in orcheckdict:
            if orcheckdict[key]:
                oridxs = pd.Series(np.array([False]*df.shape[0]))
                for idxo in orcheckdict[key]:
                    oridxs = oridxs | idxo
                idxs = idxs & oridxs
        if reset:
            df.reset_index(inplace=True, drop=True)
        df = df[idxs]
    if sort:
        df = df.sort_values(by=sortHeader,ascending=sortType)
    if reset:
        df.reset_index(inplace=True, drop=True)
    return df

if __name__ == '__main__':
    y = pd.DataFrame(dict(this=[1,2,3,4],that=[5,6,4,3]))
    y = generalFilter(y,[['this','Descending Order','','',''],
                         ['this','Contains','4','','']],reset=False)
    print y