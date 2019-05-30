#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Thu May 30 09:30:28 2019

@author: DivollHJ
"""
import os
from binascii import hexlify, unhexlify

def hexify(fname):
    with open(fname,'r') as fid:
        binry = hexlify(fid.read())
    with open('{}.txt'.format(os.path.splitext(fname)[0]),'w') as fid:
        fid.write(binry)
        
def unhexify(fname):
    with open(fname,'r') as fid:
        ascry = unhexlify(fid.read())
    with open('{}.py'.format(os.path.splitext(fname)[0]),'w') as fid:
        fid.write(ascry)     
