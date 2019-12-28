# -*- coding: utf-8 -*-
"""
Created on Sat Dec 21 15:24:53 2019

@author: HollidayHP
"""

from cx_Freeze import setup, Executable
import sys
import os
import glob
LIBPATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(LIBPATH)
sys.path.pop(0)
#sys.path.extend([_ for _ in glob.glob(os.path.join(LIBPATH,'*'))
#                 if os.path.isdir(_)])

base = None
if sys.platform == "win32":
    base = "Win32GUI"

includefiles = ['adarConfigurator.ui']
includes = []
excludes = []
packages = []

setup(name = "adarConfigurator" ,
      version = "0.1" ,
      description = "" ,
      options = {'build_exe': {'includes':includes,'excludes':excludes,
                               'packages':packages,'include_files':includefiles}},
      executables = [Executable("adarConfigurator.py",base=base)])
