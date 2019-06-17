# -*- coding: utf-8 -*-
"""
Created on Sun Jun 16 08:46:28 2019

@author: jdivoll
"""
import sys
import os

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)),'Importerator'))
import Importerator
RELATIVE_LIB_PATH = Importerator.RELATIVE_LIB_PATH
globals().update(Importerator.returnGlobals())
"""IMPORTERATOR
import pandas as pd
"""

def makeAndPrintArray():
    a = pd.DataFrame([1,2,3,4])
    print(a)