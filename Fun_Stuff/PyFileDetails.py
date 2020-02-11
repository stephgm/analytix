#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb  9 21:17:38 2020

@author: klinetry
"""
import os,sys
from six import string_types
import pandas as pd
import fnmatch

debug = True


def gather_files(sdir,**kwargs):
        '''
        Function searches a directory and subdirectories and returns all files.
        Input:
                sdir - the top directory to search through
        Kwargs:
                ext - A list of patterns -- ['*.txt','*h.h5']
                maxDepth - Restrict the maximum depth of directories to go down.

        Return:
                Returns a list of all the gathered files referenced from sdir
        '''
        extensions = kwargs.get('ext',['*'])
        maxDepth = kwargs.get('maxDepth',-1)
        if not isinstance(extensions,list):
            if debug:
                print('The ext argument you passed is not an iterable returning')
            return sdir,[]
        if not isinstance(maxDepth,int):
            if debug:
                print('the maxDepth argument you passed is not an int, going all the way down!')
            maxDepth = -1
        if maxDepth > 0:
            return sdir,[os.path.join(r,fname)[len(sdir):] for ext in extensions \
                    for r,p,f in os.walk(sdir,followlinks=False) \
                    if r[len(sdir):].count(os.sep) < maxDepth\
                    for fname in f \
                    if fnmatch.fnmatch(fname,ext)]
        elif maxDepth == 0:
            return sdir,[f for ext in extensions \
                    for f in os.listdir(sdir) \
                    if fnmatch.fnmatch(f,ext)]
        else:
            return sdir,[os.path.join(r,fname)[len(sdir):] for ext in extensions \
                for r,p,f in os.walk(sdir,followlinks=False) \
                for fname in f \
                if fnmatch.fnmatch(fname,ext)]

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
            
    def get_repo_python_files(self,repodir):
        python_files_in_repo = gather_files(repodir, ext=['*.py'])[1]
        python_files_in_repo = list(map(lambda x: x[1:].replace(os.path.sep,'.').replace('.py','').strip(),python_files_in_repo))
        
        return python_files_in_repo
    
    def get_repo_subdirs(self,repodir):
        repo_dirs = [p for p in os.listdir(repodir) if os.path.isdir(os.path.join(repodir,p))]
        return repo_dirs
        
    
    def get_imports(self,repodir=''):
        self.imports = {'Package/Module':[],'Alias':[],'Specific Imports':[]}
        if not isinstance(repodir,string_types):
            if debug:
                print('The repodir you passed is not a string.. setting to dirname of fpath')
            repodir = ''
        if not os.path.isdir(repodir):
            if debug:
                print('The repodir you passed is not a directory.. setting to dirname of fpath')
            repodir = ''
        if self.fpath and self.lines:
            if not repodir:
                repodir = os.path.dirname(self.fpath)
            repo_subdirs = self.get_repo_subdirs(repodir)
            print(repo_subdirs)
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
                        if not wordsStart[1] in repo_subdirs:
                            funcs = list(map(str.strip,wordsStart[3].split(',')))
                            self.imports['Package/Module'].append(wordsStart[1])
                            self.imports['Alias'].append(wordsEnd[1])
                            self.imports['Specific Imports'].append(funcs)
                        else: #This else is for repo imports EX from PlotH5 import Plotterator as Plotterator
                            funcs = list(map(str.strip,wordsStart[3].split(',')))
                            self.imports['Package/Module'].append(wordsStart[1]+'.'+wordsEnd[1][:asLoc])
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

    def get_repo_dependencies(self,repodir=os.path.join(os.path.expanduser('~'),'tools','src'),**kwargs):
        main = kwargs.get('main',True)
        if not isinstance(repodir,string_types):
            if debug:
                print('The repodir that you passed is not a string')
            return pd.DataFrame()
        if not os.path.isdir(repodir):
            if debug:
                print('The repodir passed is not a directory')
            return pd.DataFrame()
        python_files_in_repo = gather_files(repodir, ext=['*.py'])[1]
        python_files_in_repo = list(map(lambda x: x[1:].replace(os.path.sep,'.').replace('.py','').strip(),python_files_in_repo))
        fileimports = self.get_imports(repodir)
        idx = fileimports['Package/Module'].isin(python_files_in_repo)
        used = []
        for row,b in enumerate(idx):
            if not b:
                continue
            used.append(fileimports['Package/Module'].iloc[row])
        useddir = list(map(lambda x:os.path.join(repodir,x.replace('.',os.path.sep)+'.py'),used))
        for fpath in useddir:
            xx = Get_PyFile_Data(fpath)
            useddir += xx.get_repo_dependencies(repodir,main=False)
        if not main:
            return useddir
        else:
            return list(pd.unique(useddir))
        
# repodir = '/home/klinetry/Desktop/analytix-master/tools/src'
# fpath = os.path.join(repodir,'PlotH5','Plotter','Plotter.py')


# x = Get_PyFile_Data(fpath)  
# uu = x.get_imports(repodir)
# y = x.get_repo_dependencies(repodir)

        
        
        
        
        
        
        
        
        
        
