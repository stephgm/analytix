# -*- coding: utf-8 -*-
"""
Created on Wed Dec 19 19:47:08 2018

@author: Jordan
"""
import numpy as np

def countcrazy(num):
    for i in range(num):
        print(i)
        
def calcpi(x0,y0,num):
    x = {'pi':[],'index':[]}
    pi0 = 2. + 2.**.5
    for i in range(num):
        newx = 0.5*(x0**(.5) + x0**(-.5))
        newy = (y0*(x0**(.5)) + x0**(-.5))/(y0+1.)
        newpi = pi0*((newx+1.)/(newy+1.))
        x0 = newx
        y0 = newy
        pi0 = newpi
        x['pi'].append(pi0)
        x['index'].append(i)
    newpi = pi0*((newx+1.)/(newy+1.))
    print(newpi)
    return x

def calcPI(starter,num):
    x = {'pi':[],'index':[]}
    for i in range(num):
        newguess = starter + np.sin(starter)
        starter = newguess
        x['pi'].append(newguess)
        x['index'].append(i)
    return x