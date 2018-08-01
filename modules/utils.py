#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  1 05:04:40 2018

@author: hollidayh
"""
import time
def thisAnalysis(epath,**kwargs):
    print('here')
    print(epath)
    newvar = kwargs.pop('force',True)
    print(newvar)
    time.sleep(1)
    print('waking')