# -*- coding: utf-8 -*-
"""
Created on Sat Dec 21 15:24:53 2019

@author: HollidayHP
"""

from cx_Freeze import setup, Executable
import sys

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