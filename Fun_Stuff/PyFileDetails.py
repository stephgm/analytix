#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb  9 21:17:38 2020

@author: Carl
"""
import os,sys
from six import string_types
import pandas as pd

debug = True

class Get_PyFile_Data(object):
    def __init__(self,fpath,**kwargs):
        if not isinstance(fpath,string_types):
            if debug:
                print('The python file path you passed is not a string')
            self.fpath = ''
        else:
            self.fpath = fpath
        if not os.path.isfile(self.fpath):
            if debug:
                print('The python file is not a path')
            self.fpath = ''
            
        self.read_lines()
        self.functions = {}
        self.classes = {}
        self.classes_methods={}
        
    def read_lines(self):
        if self.fpath:
            with open(self.fpath,'r') as pf:
                self.lines = pf.readlines()
        else:
            self.lines = []
    
    def get_imports(self):
        self.imports = {'Package/Module':[],'Alias':[],'Specific Imports':[]}
        if self.fpath and self.lines:
            for line in self.lines:
                line = line.strip()
                if line.startswith('import '):
                    words = line.split()
                    if len(words) > 2 and words[2] == 'as':
                        self.imports['Package/Module'].append(words[1])
                        self.imports['Alias'].append(words[3])
                        self.imports['Specific Imports'].append('')
                    else:
                        self.imports['Package/Module'].append(words[1])
                        self.imports['Alias'].append('')
                        self.imports['Specific Imports'].append('')
                elif line.startswith('from '): # assume from x import y,z,foo
                    if ' as ' in line: # from x import y as z
                        asLoc = line.find(' as ')
                        wordsEnd = line[asLoc:].split()
                        wordsStart = line.split(None,3)
                        funcs = list(map(str.strip,wordsStart[3].split(',')))
                        self.imports['Package/Module'].append(wordsStart[1])
                        self.imports['Alias'].append(wordsEnd[1])
                        self.imports['Specific Imports'].append(funcs)
                    else: # from x import y
                        words = line.split(None,3)
                        funcs = list(map(str.strip,words[3].split(',')))
                        self.imports['Package/Module'].append(words[1])
                        self.imports['Alias'].append('')
                        self.imports['Specific Imports'].append(funcs)
        return pd.DataFrame(self.imports)
    
    def get_functions(self):
        self.functions = {'Function Name':[],'Args':[],'Line Number':[]}
        if self.fpath and self.lines:
            currentclass = ''
            classindent = 0
            for i,line in enumerate(self.lines):
                indentlevel = 0
                for char in line:
                    if char == ' ':
                        indentlevel += 1
                    else:
                        break
                line = line.strip()
                if line.startswith('class '):
                    currentclass = line.replace('class ','').split('(')[0]
                    classindent = indentlevel
                elif line.startswith('def') and indentlevel > classindent:
                    continue
                elif line.startswith('def '):
                    indentlevel = 0
                    classindent = 0
                    currentclass = ''
                    args = ''
                    func = ''
                    func,args = line.replace('def ','').split('(')[:2]
                    if args:
                        args = args.split(')')[0]
                    
                    self.functions['Function Name'].append(func)
                    self.functions['Args'].append(args)
                    self.functions['Line Number'].append(i+1)
                else:
                    continue
        return pd.DataFrame(self.functions)
    
    def get_classes(self):
        self.classes = {'Class Name':[],'Line Number':[]}
        if self.fpath and self.lines:
            for i,line in enumerate(self.lines):
                line = line.strip()
                if line.startswith('class'):
                    currentclass = line.replace('class','').split('(')[0]
                    self.classes['Class Name'].append(currentclass)
                    self.classes['Line Number'].append(i+1)
        return pd.DataFrame(self.classes)
    
    def get_class_and_methods(self):
        self.classes_methods = {'Class Name':[],'Method':[],'Args':[],'Line Number':[]}
        if self.fpath and self.lines:
            currentclass = ''
            classindent = 0
            for i,line in enumerate(self.lines):
                indentlevel = 0
                for char in line:
                    if char == ' ':
                        indentlevel += 1
                    else:
                        break
                line = line.strip()
                if line.startswith('class'):
                    currentclass = line.replace('class ','').split('(')[0]
                    classindent = indentlevel
                elif line.startswith('def') and indentlevel > classindent:
                    self.classes_methods['Class Name'].append(currentclass)
                    func = ''
                    args = ''
                    func,args = line.replace('def ','').split('(')[:2]
                    if args:
                        args = args.split(')')[0]
                    self.classes_methods['Method'].append(func)
                    self.classes_methods['Args'].append(args)
                    self.classes_methods['Line Number'].append(i+1)
                else:
                    continue
                indentlevel = 0
        return pd.DataFrame(self.classes_methods)
                    
    def get_outline(self):
        if not self.classes_methods:
            y = self.get_class_and_methods()
        else:
            y = pd.DataFrame(self.classes_methods)
        if not self.functions:
            x = self.get_functions()
        else:
            x = pd.DataFrame(self.functions)
        colorder = ['Function Name','Class Name','Method','Args','Line Number']
        return pd.concat([y,x],sort=False).sort_values('Line Number')[colorder]
    
    def get_what_calls_what(self):
        '''
        Needs to be smarter.. shouldn't be ran
        '''
        self.what_calls_what = {'Source':[],'Target':[],'Source Type':[],'Target Type':[],'Source Class':[],'Target Class':[],'Line Number':[]}
        if self.fpath and self.lines:
            outline = self.get_outline()
            outline['Class Name'] += '('
            outline['Method'] += '('
            outline['Function Name'] += '('
            
            currentclass = ''
            classindent = 0
            currentdef = ''
            for i,line in enumerate(self.lines):
                indentlevel = 0
                for char in line:
                    if char == ' ':
                        indentlevel += 1
                    else:
                        break
                line = line.strip()
                if line.startswith('class '):
                    currentclass = line.replace('class ','').split('(')[0]
                    classindent = indentlevel
                    continue
                elif line.startswith('def') and indentlevel > classindent:
                    func = ''
                    args = ''
                    currentdef,args = line.replace('def ','').split('(')[:2]
                    if args:
                        args = args.split(')')[0]
                    continue
                elif line.startswith('def '):
                    indentlevel = 0
                    classindent = 0
                    currentclass = ''
                    args = ''
                    func = ''
                    currentdef,args = line.replace('def ','').split('(')[:2]
                    if args:
                        args = args.split(')')[0]
                    continue
                if currentdef and isinstance(currentdef,string_types) and currentdef.startswith('__') and currentdef.endswith('__'):
                    continue
                idx1 = pd.Series(list(map(lambda x: True if isinstance(x,string_types) and x in line else False,outline['Function Name'])))
                idx2 = pd.Series(list(map(lambda x: True if isinstance(x,string_types) and x in line else False,outline['Method'])))
                idx = (idx1) | (idx2)
                for row,b in enumerate(idx):
                    if not b:
                        continue
                    FuncName = outline.iloc[row]['Function Name']
                    MethodName = outline.iloc[row]['Method']
                    ClassName = outline.iloc[row]['Class Name']
                    # if MethodName and isinstance(MethodName,string_types) and MethodName.startswith('__') and MethodName.endswith('__'):
                        # continue
                    if FuncName and isinstance(FuncName,string_types):
                        if FuncName in line:
                            self.what_calls_what['Source'].append(currentdef)
                            self.what_calls_what['Target'].append(FuncName[:-1])
                            if currentclass:
                                self.what_calls_what['Source Type'].append('Class Method')
                            else:
                                self.what_calls_what['Source Type'].append('Function')
                            self.what_calls_what['Target Type'].append('Function')
                            self.what_calls_what['Source Class'].append(currentclass)
                            self.what_calls_what['Target Class'].append('')
                            self.what_calls_what['Line Number'].append(i+1)
                    elif MethodName and isinstance(MethodName,string_types):
                        if MethodName in line:
                            self.what_calls_what['Source'].append(currentdef)
                            self.what_calls_what['Target'].append(MethodName[:-1])
                            if currentclass:
                                self.what_calls_what['Source Type'].append('Class Method')
                            else:
                                self.what_calls_what['Source Type'].append('Function')
                            self.what_calls_what['Target Type'].append('Class Method')
                            self.what_calls_what['Source Class'].append(currentclass)
                            self.what_calls_what['Target Class'].append(ClassName)
                            self.what_calls_what['Line Number'].append(i+1)
                            
        return pd.DataFrame(self.what_calls_what)

