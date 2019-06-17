# -*- coding: utf-8 -*-
"""
Created on Sun Jun 16 08:50:18 2019

@author: jdivoll
"""
import sys
import os

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)),'Importerator'))
import Importerator
RELATIVE_LIB_PATH = Importerator.RELATIVE_LIB_PATH
globals().update(Importerator.returnGlobals())
"""IMPORTERATOR
IMPORTERATOR_FROM_REPO
import testimports as tits
"""

def deeperNdeeper():
    tits.makeAndPrintArray()