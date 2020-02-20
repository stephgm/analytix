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
import numpy as np
from shutil import copyfile,rmtree

debug = True


def gather_files2(sdir,**kwargs):
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

class Get_PyFile_Data2(object):
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
            self.lines = [line for line in self.lines if not self.isCommentLine(line)]
                
        else:
            self.lines = []
    
    def isCommentLine(self,line):
        line = line.strip()
        if line.startswith('#'):
            return True
        else:
            return False
            
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
                            WordsStartAsLoc = wordsStart[-1].find(' as ')
                            self.imports['Package/Module'].append(wordsStart[1]+'.'+wordsStart[-1][:WordsStartAsLoc])
                            self.imports['Alias'].append(wordsEnd[1])
                            self.imports['Specific Imports'].append(funcs)
                    else: # from x import y
                        words = line.split(None,3)
                        funcs = list(map(str.strip,words[3].split(',')))
                        if words[1] not in repo_subdirs:
                            self.imports['Package/Module'].append(words[1])
                            self.imports['Alias'].append('')
                            self.imports['Specific Imports'].append(funcs)
                        else:
                            print(words)
                            for f in funcs:
                                self.imports['Package/Module'].append(words[1]+'.'+f)
                                self.imports['Alias'].append('')
                                self.imports['Specific Imports'].append(f)
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
    
    def get_UI_file_dependencies(self):
        ui_files = []
        if self.fpath and self.lines:
            for line in self.lines:
                if ".ui'" in line:
                    last_quote_pos = line.find(".ui'")
                    if last_quote_pos > 0:
                        last_quote_pos+=3
                    for i,char in enumerate(line[:last_quote_pos]):
                        if char == "'":
                            first_quote_pos = i+1
                elif '.ui"' in line:
                    last_quote_pos = line.find('.ui"')
                    if last_quote_pos:
                        last_quote_pos+=3
                    for i,char in enumerate(line[:last_quote_pos]):
                        if char == '"':
                            first_quote_pos = i+1
                else:
                    continue
                ui_file = line[first_quote_pos:last_quote_pos]
                ui_files.append(os.path.join(os.path.dirname(self.fpath),ui_file))
        return ui_files
    def get_any_file_mention(self,repodir):
        mentioned_files = []
        if self.fpath and self.lines:
            all_files = gather_files(repodir)
            all_fpaths = list(map(lambda x:os.path.join(all_files[0],x),all_files[1]))
            for line in self.lines:
                for fpath in all_fpaths:
                    if os.path.basename(fpath) in line:
                        mentioned_files.append(fpath)
        return mentioned_files
    
    def get_file_repo_dependencies(self,repodir=os.path.join(os.path.expanduser('~'),'tools','src'),initusedfiles=[],**kwargs):
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
        fileimports = self.get_any_file_mention(repodir)
        idx = fileimports['Package/Module'].isin(python_files_in_repo)
        used = []
        for row,b in enumerate(idx):
            if not b:
                continue
            used.append(fileimports['Package/Module'].iloc[row])
        #Get file path of the used python files in the fpath
        usedfile = list(map(lambda x:os.path.join(repodir,x.replace('.',os.path.sep)+'.py'),used))
        #if incoming used files differ from this usedfile get more
        if set(usedfile).difference(set(initusedfiles)):
            newused = list(set(usedfile).difference(set(initusedfiles)))
            #add difference to the incoming used files
            initusedfiles += newused
            for fpath in newused:
                xx = Get_PyFile_Data(fpath)
                moreusedfile = xx.get_file_repo_dependencies(repodir,initusedfiles,main=False)
                initusedfiles += moreusedfile
                initusedfiles = list(pd.unique(initusedfiles))
            initusedfiles += self.get_UI_file_dependencies()
        return list(pd.unique(initusedfiles))

    def isolate_file_repo_dependencies(self,repodir=os.path.join(os.path.expanduser('~'),'tools','src'),outdir=''):
        #This doesn't grab all of the dependencies??? Not sure why...
        if not outdir:
            outdir = os.path.join(os.path.expanduser('~'),f'{os.path.basename(self.fpath).split(".py")[0]}_dependencies','tools','src')
        if not os.path.isdir(outdir):
            os.makedirs(outdir)
        else:
            print('You are trying to create an outdir that already exists... reconsider for safety')
            print('Continuing anyways...')
            # choice = input(f'Do you want to delete {outdir} and recreate it with the repo dependencies?')
            # if choice:
            #This is dangerous if not used correctly.. will just print a statement
                # rmtree(outdir)
                # os.makedirs(outdir)
            # else:
                # return
        files_to_move = self.get_file_repo_dependencies(repodir,[])
        files_to_move.append(self.fpath)
        # return files_to_move
        for file in files_to_move:
            if os.path.isfile(file):
                nfpath = os.path.join(outdir,file.replace(repodir,'')[1:])
                if not os.path.isdir(os.path.dirname(nfpath)):
                    os.makedirs(os.path.dirname(nfpath))
                copyfile(file, nfpath)
            else:
                print(f'{file} did not exist... continuing')
                
        
        
        
        
        
        
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
import numpy as np
from shutil import copyfile,rmtree
import compileall
import pathlib

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
            return sdir,[os.relpath(os.path.join(r,fname),sdir) for ext in extensions \
                    for r,p,f in os.walk(sdir,followlinks=False) \
                    if r[len(sdir):].count(os.sep) < maxDepth\
                    for fname in f \
                    if fnmatch.fnmatch(fname,ext)]
        elif maxDepth == 0:
            return sdir,[f for ext in extensions \
                    for f in os.listdir(sdir) \
                    if fnmatch.fnmatch(f,ext)]
        else:
            return sdir,[os.path.relpath(os.path.join(r,fname),sdir) for ext in extensions \
                for r,p,f in os.walk(sdir,followlinks=False) \
                for fname in f \
                if fnmatch.fnmatch(fname,ext)]

class Get_PyFile_Data(object):
    def __init__(self,fpath,repodir='',**kwargs):
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
        if not isinstance(repodir,string_types):
            if debug:
                print('The repodir you passed is not a string')
            self.repodir = ''
        else:
            self.repodir = repodir
        if not os.path.isdir(self.repodir):
            if debug:
                print('The repodir you passed is not a directory')
            self.repodir = ''
            
        self.read_lines()
        self.functions = pd.DataFrame()
        self.classes = pd.DataFrame()
        self.classes_methods= pd.DataFrame()
        self.imports = pd.DataFrame()
        self.repo_imports = pd.DataFrame()
        self.outline = pd.DataFrame()
        self.what_calls_what_internal = pd.DataFrame()
        self.mentioned_files = []
        
        self.parse_file()
        
    def read_lines(self):
        if self.fpath:
            with open(self.fpath,'r') as pf:
                self.lines = pf.readlines()
            self.lines = [line for line in self.lines if not self.isCommentLine(line)]
                
        else:
            self.lines = []
    
    def isCommentLine(self,line):
        line = line.strip()
        if line.startswith('#'):
            return True
        else:
            return False
            
    def get_import_format_python_files(self):
        python_files_in_repo = []
        if self.repodir:
            python_files_in_repo = gather_files(self.repodir, ext=['*.py'])[1]
            python_files_in_repo = list(map(lambda x: x.replace(os.path.sep,'.').replace('.py','').strip(),python_files_in_repo))
        return python_files_in_repo
    
    def get_python_files(self):
        return gather_files(repodir,ext=['*.py'])[1]
    
    def get_repo_subdirs(self):
        repo_subdirs = []
        if self.repodir:
            for p,dirs,files in os.walk(self.repodir):
                repo_subdirs += list(map(lambda x:os.path.relpath(os.path.join(p,x),self.repodir),dirs))
        return repo_subdirs
    
    def get_import_format_repo_subdirs(self):
        repo_dirs = []
        if self.repodir:
            for p, dirs, files in os.walk(repodir):
                repo_dirs += list(map(lambda x:os.path.relpath(os.path.join(p,x),repodir).replace(os.sep,'.'),dirs))
        return repo_dirs
    
    def get_all_files_names_in_repo(self):
        if self.repodir:
            return list(map(os.path.basename,gather_files(self.repodir)[1]))
    
    def get_all_files_paths_in_repo(self):
        if self.repodir:
            basepath,file_list = gather_files(self.repodir)
            return list(map(lambda x:os.path.join(basepath,x),file_list))
    
    def parse_file(self,**kwargs):
        if self.fpath and self.repodir and self.lines:
            import_style_subdirs = self.get_import_format_repo_subdirs()
            import_style_files = self.get_import_format_python_files()
            all_files_paths = self.get_all_files_paths_in_repo()
            
            currentclass = ''
            classindent = 0
            
            repo_imports = {'Repo Imports':[]}
            
            imports = {'Package/Module':[],'Alias':[],'Specific Imports':[]}
            
            classes_methods = {'Class Name':[],'Method':[],'Args':[],'Line Number':[]}
            functions = {'Function Name':[],'Args':[],'Line Number':[]}
            classes = {'Class Name':[],'Line Number':[]}
            
            mentioned_files = []
            
            for i,line in enumerate(self.lines):
                indentlevel = 0
                for char in line:
                    if char == ' ':
                        indentlevel += 1
                    else:
                        break
                
                line = line.strip()
                words = line.split()
                #This is the repo_dependent imports of the file section

                if 'import' in line:
                    for word in words:
                        if word in import_style_subdirs:
                            for otherword in words:
                                if word == otherword:
                                    continue
                                if f'{word}.{otherword}' in import_style_files:
                                    repo_imports['Repo Imports'].append(f'{word}.{otherword}')
                        if word in import_style_files:
                            repo_imports['Repo Imports'].append(word)
                
                #This is the regular imports section
                
                if line.startswith('import '):
                    if len(words) > 2 and words[2] == 'as':
                        imports['Package/Module'].append(words[1])
                        imports['Alias'].append(words[3])
                        imports['Specific Imports'].append('')
                    else:
                        imports['Package/Module'].append(words[1])
                        imports['Alias'].append('')
                        imports['Specific Imports'].append('')
                elif line.startswith('from '): # assume from x import y,z,foo
                    if ' as ' in line: # from x import y as z
                        asLoc = line.find(' as ')
                        wordsEnd = line[asLoc:].split()
                        wordsStart = line.split(None,3)
                        funcs = list(map(str.strip,wordsStart[3].split(',')))
                        imports['Package/Module'].append(wordsStart[1])
                        imports['Alias'].append(wordsEnd[1])
                        imports['Specific Imports'].append(funcs)
                    else: # from x import y
                        words = line.split(None,3)
                        funcs = list(map(str.strip,words[3].split(',')))
                        imports['Package/Module'].append(words[1])
                        imports['Alias'].append('')
                        imports['Specific Imports'].append(funcs)
                        
                #This is the class, class method, and def parsing
                if line.startswith('class '):
                    currentclass = line.replace('class ','').split('(')[0]
                    classindent = indentlevel
                    classes['Class Name'].append(currentclass)
                    classes['Line Number'].append(i+1)
                    
                elif line.startswith('def') and indentlevel > classindent:
                    classes_methods['Class Name'].append(currentclass)
                    func = ''
                    args = ''
                    func,args = line.replace('def ','').split('(')[:2]
                    if args:
                        args = args.split(')')[0]
                    classes_methods['Method'].append(func)
                    classes_methods['Args'].append(args)
                    classes_methods['Line Number'].append(i+1)
                    
                elif line.startswith('def ') and indentlevel <= classindent:
                    indentlevel = 0
                    classindent = 0
                    currentclass = ''
                    args = ''
                    func = ''
                    func,args = line.replace('def ','').split('(')[:2]
                    if args:
                        args = args.split(')')[0]
                    
                    functions['Function Name'].append(func)
                    functions['Args'].append(args)
                    functions['Line Number'].append(i+1)
                
                #This section makes a list of any file mentioned in the pyfile that is also in the repo
                for fpath in all_files_paths:
                    if os.path.basename(fpath) in line:
                        mentioned_files.append(fpath)
            self.imports = pd.DataFrame(imports)
            self.repo_imports = pd.DataFrame(repo_imports)
            self.repo_imports.drop_duplicates(inplace=True)
            self.repo_imports.reset_index(drop=True,inplace=True)
            self.classes_methods = pd.DataFrame(classes_methods)
            self.functions = pd.DataFrame(functions)
            self.classes = pd.DataFrame(classes)
            self.mentioned_files = list(pd.unique(mentioned_files))

        return self.imports,self.repo_imports,self.classes_methods,self.functions,self.classes,self.mentioned_files               
        
    def get_repo_imports_from_file(self,**kwargs):
        if not self.repo_imports.shape[0]:
            self.parse_file()
        return self.repo_imports
    
    def get_repo_import_paths(self,**kwargs):
        df = self.get_repo_imports_from_file()
        xx = df['Repo Imports'].apply(lambda x: os.path.join(self.repodir,x).replace('.',os.path.sep)+'.py')
        return xx.to_list()
    
    def get_imports(self):
        if not self.imports.shape[0]:
            self.parse_file()
        return self.imports
    
    def get_functions(self):
        if not self.functions.shape[0]:
            self.parse_file()
        return self.functions
    
    def get_classes(self):
        if not self.classes.shape[0]:
            self.parse_file()
        return self.classes
    
    def get_class_and_methods(self):
        if not self.classes_methods.shape[0]:
            self.parse_file()
        return self.classes_methods
                    
    def get_outline(self):
        y = self.get_class_and_methods()
        x = self.get_functions()
        colorder = ['Function Name','Class Name','Method','Args','Line Number']
        self.outline = pd.concat([y,x],sort=False).sort_values('Line Number')
        self.outline = self.outline[colorder]
        return self.outline
    
    def get_what_calls_what_internal(self):
        if self.what_calls_what_internal.shape[0]:
            return self.what_calls_what_internal
        what_calls_what = {'Source':[],'Target':[],'Source Type':[],'Target Type':[],'Source Class':[],'Target Class':[],'Line Number':[]}
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
                            what_calls_what['Source'].append(currentdef)
                            what_calls_what['Target'].append(FuncName[:-1])
                            if currentclass:
                                what_calls_what['Source Type'].append('Class Method')
                            else:
                                what_calls_what['Source Type'].append('Function')
                            what_calls_what['Target Type'].append('Function')
                            what_calls_what['Source Class'].append(currentclass)
                            what_calls_what['Target Class'].append('')
                            what_calls_what['Line Number'].append(i+1)
                    elif MethodName and isinstance(MethodName,string_types):
                        if MethodName in line:
                            what_calls_what['Source'].append(currentdef)
                            what_calls_what['Target'].append(MethodName[:-1])
                            if currentclass:
                                what_calls_what['Source Type'].append('Class Method')
                            else:
                                what_calls_what['Source Type'].append('Function')
                            what_calls_what['Target Type'].append('Class Method')
                            what_calls_what['Source Class'].append(currentclass)
                            what_calls_what['Target Class'].append(ClassName)
                            what_calls_what['Line Number'].append(i+1)
                            
        self.what_calls_what_internal = pd.DataFrame(what_calls_what)
        return self.what_calls_what_internal
    
                
    
        
repodir = '/home/klinetry/Desktop/analytix-master/tools/src'
fpath = os.path.join(repodir,'PlotH5','Plotter','Plotter.py')

# repodir = '/home/klinetry/Desktop/shitrepo'
# fpath = os.path.join(repodir,'RUTE.py')

# x = Get_PyFile_Data(fpath)  
# uu = x.get_imports(repodir)
# y = x.get_file_repo_dependencies(repodir,[])
# ii = x.isolate_file_repo_dependencies(repodir)  


def get_repo_imports_from_file(fpath,repodir,currentfilelist=set()):
    xx = Get_PyFile_Data(fpath,repodir)
    usedfiles = set()
    usedfiles.update(xx.get_repo_import_paths())
    usedfiles.update(xx.mentioned_files)
    newused = usedfiles - currentfilelist
    if newused:
        currentfilelist.update(newused)
        for nfpath in newused:
            if os.path.splitext(nfpath)[-1] == '.py':
                mfiles = get_repo_imports_from_file(nfpath,repodir,currentfilelist)
                currentfilelist.update(mfiles)
        
    return currentfilelist

def isolate_repo_dependencies(fpath,repodir):
    outdir = os.path.join(os.path.expanduser('~'),os.path.splitext(os.path.basename(fpath))[0]+'_depends','tools','src')
    if os.path.isdir(outdir):
        rmtree(outdir)
    os.makedirs(outdir)
    #get all of the file mentions from everything
    ftm = get_repo_imports_from_file(fpath, repodir)
    #add the file that we are wanting to isolate..
    ftm.add(fpath)
    for file in ftm:
        if os.path.isfile(file):
            nfpath = os.path.join(outdir,os.path.relpath(file,repodir))
            if not os.path.isdir(os.path.dirname(nfpath)):
                os.makedirs(os.path.dirname(nfpath))
            copyfile(file,nfpath)
        else:
            print(f'{file} did not exist..continuing')
    #byte compile all the stuff
    compileall.compile_dir(outdir,force=True)
    for p,d,f in os.walk(outdir):
        
        #move the pyc files up one directory out of the __pycache__ folder
        if '__pycache__' in p:
            for file in f:
                o = pathlib.Path(os.path.join(p,file)).absolute()
                parent_dir = o.parents[1]
                o.rename(parent_dir / o.name.replace('.cpython-37',''))
        #get rid of the regular .py files
        else:
            for file in f:
                if os.path.splitext(file)[-1] == '.py':
                    os.remove(os.path.join(p,file))
    
    #go back through and delete empty dirs
    for p,d,f in os.walk(outdir):
        if not d and not f:
            rmtree(p)
    
    
h = isolate_repo_dependencies(fpath, repodir)
        
    
        
        
        
        
        
        
        
        
        
