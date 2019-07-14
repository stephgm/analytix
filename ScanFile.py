# -*- coding: utf-8 -*-
"""
Created on Sun Jul 14 01:57:22 2019

@author: Jordan
"""

import inspect
import sys
import os
import glob2
import copy
import importlib

def scanFile(pyfile,repodir):
    repodir = os.path.dirname(repodir)
    sys.path.extend(glob2.glob(os.path.join(repodir,"**","**")))
    fid = open(pyfile,'rb')
    lines = fid.readlines()
    lines = map(lambda x: x.strip(), lines)
    quotinBig = False
    quotinSmall = False
    val = []
    for i,line in enumerate(lines):
        if (line.strip().startswith('"""') or line.strip().endswith('"""')) and line.find('IMPORTERATOR') == -1:
            if not quotinBig:
                quotinBig = True
            else:
                quotinBig = False
        if line.strip().startswith("'''") or line.strip().endswith("'''"):
            if not quotinSmall:
                quotinSmall = True
            else:
                quotinSmall = False
        if line.find('import') != -1 and not (quotinBig or quotinSmall):
            value = parseImport(line,i)
            for j in range(len(value)):
                if value[j][0]:
                    print value[j]
                    val.extend(list([value[j]]))
#    return
    for statement in val:
#        print 'importing {}'.format(statement[0])
#        imported = __import__(statement[0])
        imported = importlib.import_module(statement[0], package=None)
        linenums = getLineNums(statement,val)
        if len(linenums) > 1:
            print 'import {} on line number {} seems to be imported multiple times'.format(statement[0],statement[2]+1)
        copylines = getLines(lines,linenums)
        findthiswith = []
        if statement[1][0] and not statement[1][1]:
            lookdeeper = True
            findthis = statement[1][0]
        elif not statement[1][0] and statement[1][1]:
            lookdeeper = False
            findthis = statement[1][1]
        else:
            lookdeeper = True
            findthis = statement[0]
#        checker = 'ccrs'
        if lookdeeper:
            findthiswith = [o[0] for o in inspect.getmembers(imported) if ((callable(o[1])) and not o[0].startswith('_'))]
        breakmain = False
        FOUND=False
        for line in copylines:
            #need to add more logic here TODO if import after ''' or ignore everything after a # thats not in quotes.
            if line.startswith("'''") or line.startswith('#'):
                continue
            if findthiswith:
                searchstring = findthis+'.'
#                print searchstring
                if searchstring in line:
#                    if findthis == checker:
#                        print searchstring
                    FOUND = True
                    breakmain = True
                    break
                for thing in findthiswith:
                    searchstring = findthis+'.'+thing+'('
                    searchstring2 = findthis+'.'+thing+'.'
#                    if findthis == checker:
#                        print searchstring,searchstring2
#                    print searchstring
                    if searchstring in line or searchstring2 in line:
                        FOUND=True
                        breakmain = True
                        break
                if breakmain:
                    break
            else:
                searchstring = findthis+'('
                searchstring2 = findthis+'.'
                searchstring3 = findthis+'.'+thing+'.'
#                if findthis == checker:
#                    print searchstring
                if searchstring in line or searchstring2 in line or searchstring3 in line:
                    FOUND=True
                    break
        if not FOUND:
            print 'import {}.{} on line {} does not seem to be used.'.format(statement[0],statement[1][1],statement[2]+1)
        
#    cPickle.dump(thedict,
#                 file(os.path.join(os.path.dirname(os.path.realpath(__file__)),'theimports.pkl'),'wb'),
#                 protocol=cPickle.HIGHEST_PROTOCOL)
            
def getLines(lines,linenums):
    clines = copy.copy(lines)
    for num in reversed(linenums):
        clines.pop(num)
    return clines

def getLineNums(statement,statements):
    linenums = []
    for lstatement in statements:
        if statement == lstatement:
            linenums.append(lstatement[2])
    return sorted(linenums)
                
def parseImport(line,linenum):
    line = line.strip()
    if line.startswith('import '):
        words = line.split()
        if len(words) > 2 and words[2] == 'as':
            return [[words[1],(words[3],()),linenum]]
        else:
            return [[words[1],('',()),linenum]]
    elif line.startswith('from '): # assume from x import y,z,foo
        multiport = []
        if ' as ' in line: # from x import y as z
            asLoc = line.find(' as ')
            wordsEnd = line[asLoc:].split()
            wordsStart = line.split(None,3)
            for word in wordsStart[3].split(','):
                word = word.strip()
                multiport.append([wordsStart[1],(wordsEnd[1],word),linenum])
            return multiport
        else: # from x import y  #TODO support for from x import y as z and from x import u as z, w as y and from x import u, z as y
            words = line.split(None,3)
            for word in words[3].split(','):
                word = word.strip()
                multiport.append([words[1],('',word),linenum])
            return multiport
    else:
        return [['',[],linenum]]
    
if __name__ == '__main__':
    
#    repodir = os.path.join(os.path.expanduser('~'),'Desktop','RandomRepo')
    repodir = os.path.join(os.path.expanduser('~'),'Desktop','analytix-master')
#    pyfile = os.path.join(repodir,'Steel','Tir.py')
    pyfile = os.path.join(repodir,'Plotter','Plotter.py')
    scanFile(pyfile,repodir)