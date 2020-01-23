#cython: language_level=3
"""
Created on Wed Jan 22 20:47:05 2020

@author: hollidayh
"""
import numpy

def printFunction():
    print('this')

def numpyFunction():
    a = numpy.arange(10)
    a *= 100
    print(a)