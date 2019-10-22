#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 20 03:47:45 2019

@author: Jordan
"""

import pandas as pd
import traceback
import sys
import os
import time
import datetime
from six import string_types
from collections import OrderedDict
import inspect
import copy

global g
# Could put this shit in a server file and just make the server do this.. could
# do html... could do whatever really.
def color_strings(column):
    '''
    Color application to status column in logging df
    '''
    if column.name == 'Status':
        idx = column == 'Failed'
        return ['color: red' if v else 'color: green' for v in idx]
    else:
        return ['color: black']*column.shape[0]

def makeLog(df,**kwargs):
    '''
    This is obviously going to slow down this simple function because it is
    reading and writing to the disk.... NOT THE SOLUTION just PROOF OF CONCEPT
    This is hacked up more than a dead body in a Friday the 13th film.
    '''
    df = pd.DataFrame(df)
    print df
    fpath = os.path.join(os.path.expanduser('~'),'test.xlsx')
    if not os.path.isfile(fpath):
        p = pd.DataFrame(columns=list(df))
        p.to_excel(fpath,index=False)
    yy = pd.read_excel(fpath)
    yy = pd.concat([yy,df],ignore_index=True)
    yy.reset_index(drop=True,inplace=True)
    yy = yy.style.apply(color_strings)
    yy.to_excel(excel_writer = fpath,index=False)


class logger(object):
    def __init__(self,func):
        self.func = func
        self.initialize()

    def initialize(self):
        self.loggingInfo = OrderedDict()
        self.loggingInfo['Function'] = []
        self.loggingInfo['Status'] = []
        self.loggingInfo['args'] = []
        self.loggingInfo['kwargs'] = []
        self.loggingInfo['Signature'] = []
        self.loggingInfo['User'] = []
        self.loggingInfo['Timestamp'] = []
        self.loggingInfo['Exception'] = []
        self.loggingInfo['SubLog'] = []

    def makeLogging(self,exc='None',status='Failed',sublog='T'):
#        print sublog
        self.loggingInfo['Function'].append(self.func.__name__)
        args_repr = [repr(arg) for arg in self.ARGS]
        kwargs_repr = ['{}={}'.format(k,v) for k,v in self.KWARGS.items()]
        signature = ', '.join(args_repr + kwargs_repr)
        self.loggingInfo['Signature'].append(signature)
        self.loggingInfo['args'].append(args_repr)
        self.loggingInfo['kwargs'].append(kwargs_repr)
        self.loggingInfo['User'].append(os.path.basename(os.path.expanduser('~')))
        self.loggingInfo['Timestamp'].append(str(datetime.datetime.now()))
        self.loggingInfo['Exception'].append(exc)
        self.loggingInfo['Status'].append(status)
        self.loggingInfo['SubLog'].append(sublog)
#        print 'logged'

    def __call__(self,*args,**kwargs):
        self.initialize()
        self.ARGS = args
        self.KWARGS = copy.copy(kwargs)
        kwargs['LOGGING'] = self
        try:
            value = self.func(*args,**kwargs)
            exc = 'None'
            status = 'Successful'
        except Exception as e:
            exc_type,exc_obj,exc_tb = sys.exc_info()
            exc = '{} -> Line:{}'.format(exc_type,exc_tb.tb_lineno)
            status = 'Failed'
        self.makeLogging(exc,status,'F')
        print self.loggingInfo
        makeLog(self.loggingInfo)
        if status == 'Failed':
            raise
        return value

    def logExtra(self):
        self.makeLogging('None','Failed','T')
        return

# This is the decorator function
def status(func):
    def wrapper(*args,**kwargs):
        y = pd.DataFrame(columns=['Function','Status','args','kwargs','Signature','User','Timestamp','Exception','SubLog'])
        args_repr = [repr(a) for a in args]
        kwargs_repr = ['{}={}'.format(k,v) for k, v in kwargs.items()]
        signature = ', '.join(args_repr + kwargs_repr)
#        print('Calling {}({})'.format(func.__name__,signature))
        y['Function'] = [func.__name__]
        y['Signature'] = [signature]
        y['args'] = [args_repr]
        y['kwargs'] = [kwargs_repr]
        y['User'] = [os.path.basename(os.path.expanduser('~'))]
        y['Timestamp'] = [str(datetime.datetime.now())]
        y['SubLog'] = ['F']
        try:
            value = func(*args, **kwargs)
            y['Exception'] = ['None']
            y['Status'] = ['Successful']
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            y['Exception'] = ['{} -> Line:{}'.format(exc_type,exc_tb.tb_lineno)]
            y['Status'] = ['Failed']
        makeLog(y)
        if y['Status'].iloc[0] == 'Failed':
            raise
#        print('{} returned {}'.format(func.__name__,value))
        return value
    return wrapper

def subLog():
    y = pd.DataFrame(columns=['Function','Status','args','kwargs','Signature','User','Timestamp','Exception','SubLog'])
    y['Function'] = [inspect.stack()[1][3]]
    y['Signature'] = ['']
    y['args'] = ['']
    y['kwargs'] = ['']
    y['User'] = [os.path.basename(os.path.expanduser('~'))]
    y['Timestamp'] = [str(datetime.datetime.now())]
    y['SubLog'] = ['T']
    y['Exception'] = ['None']
    y['Status'] = ['Failed']
    makeLog(y)
# Trying out the decorator for logging.
@logger
def test(x,y,**kwargs):
    if True:
        LOGGING=kwargs.get('LOGGING',None)
        LOGGING.logExtra()
    r = float(x)/float(y)
    print r
    return r

if __name__ == '__main__':
    '''
    YES, this is slow.. but it is just a proof of concept.... can easily speed
    this sheet the fudge up....
    '''
    for i in range(25):
        if i%3 == 0:
            x = 40
            y = 0
        else:
            x = i
            y = i**2
        try:
            xx = test(x,y)
        except:
            pass