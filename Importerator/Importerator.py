# -*- coding: utf-8 -*-
"""
Created on Fri Jun 14 13:22:38 2019

@author: DivollHJ
"""
import sys
import os
import cPickle
import copy
if not hasattr(sys,'frozen'):
    RELATIVE_LIB_PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    sys.path.append(RELATIVE_LIB_PATH)
else:
    RELATIVE_LIB_PATH = os.path.dirname(sys.eexecutable)

def scanSource(srcdir):
    thedict = {}
    srcdirlen = len(srcdir)
    for root, dirs, files in os.walk(srcdir):
        for xfile in files:
            if os.path.splitext(xfile)[1] == '.py':
                with open(os.path.join(root,xfile),'r') as fid:
                    lines = fid.read().splitlines()
                thedict[os.path.join(root[srcdirlen+1:],os.path.splitext(xfile)[0])] = []
                appender = thedict[os.path.join(root[srcdirlen+1:],os.path.splitext(xfile)[0])].append
                quotinBig = False
                quotinSmall = False
                for line in lines:
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
                        val = parseImport(line)
                        if val:
                            appender(val)
    cPickle.dump(thedict,
                 file(os.path.join(os.path.dirname(os.path.realpath(__file__)),'theimports.pkl'),'wb'),
                 protocol=cPickle.HIGHEST_PROTOCOL)

def gatherImportsFromRepo(srcdir):
    thedict = {}
    srcdirlen = len(srcdir)
    for root, dirs, files in os.walk(srcdir):
        for xfile in files:
            if os.path.splitext(xfile)[1] == '.py':
                with open(os.path.join(root,xfile),'r') as fid:
                    lines = fid.read().splitlines()
                thedict[os.path.join(root[srcdirlen+1:],os.path.splitext(xfile)[0])] = {'stack':{},
                                                                                        'repo':{}}
                sdict = thedict[os.path.join(root[srcdirlen+1:],os.path.splitext(xfile)[0])]['stack']
                rdict = thedict[os.path.join(root[srcdirlen+1:],os.path.splitext(xfile)[0])]['repo']
                startGathering = False
                stacking = True
                for line in lines:
                    if line.strip().startswith('"""') and line.find('IMPORTERATOR') != -1:
                        startGathering = True
                    elif startGathering and line.find('IMPORTERATOR_FROM_REPO') != -1:
                        stacking = False
                    elif line.find('import') != -1 and startGathering:
                        val, tup = parseImport(line)
                        if val:
                            if stacking:
                                if val not in sdict:
                                    sdict[val] = []
                                sdict[val].append(tup)
                            else:
                                if val not in rdict:
                                    rdict[val] = []
                                rdict[val].append(tup)
                    elif line.strip().startswith('"""') and startGathering:
                        break
                    
    cPickle.dump(thedict,
                 file(os.path.join(os.path.dirname(os.path.realpath(__file__)),'theimports.pkl'),'wb'),
                 protocol=cPickle.HIGHEST_PROTOCOL)
             
def parseImport(line):
    line = line.strip()
    if line.startswith('import'):
        words = line.split()
        if len(words) > 2 and words[2] == 'as':
            return words[1],(words[3],())
        else:
            return words[1],('',())
    elif line.startswith('from'): # assume from x import y,z,foo
        words = line.split(None,3)
        funcs = map(str.strip,words[3].split(','))
        return words[1],('',tuple(funcs))
    else:
        return '',[]

def buildDepends(key):
    thedict = cPickle.load(file(os.path.join(os.path.dirname(os.path.realpath(__file__)),'theimports.pkl'),'rb'))
    basekeys = {os.path.basename(k):k for k in thedict}
    stackdepends = []#copy.deepcopy(thedict[key]['stack'])
    stackdict = {}
    repodepends = []#copy.deepcopy(thedict[key]['repo'])
    repodict = {}
    importedBy = {}
    
    paths_to_add = walkDepends(thedict,key,basekeys,importedBy,repodepends,stackdepends,repodict,stackdict)
    if os.path.basename(key) != key:
        paths_to_add.add(os.path.dirname(key))
    sys.path.extend([os.path.join(RELATIVE_LIB_PATH,newpath) for newpath in paths_to_add])

    for l in copy.deepcopy(repodepends):
        if l in importedBy:
            ind = len(repodepends)
            for j in importedBy[l]:
                if j in repodepends:
                    newind = repodepends.index(j)
                    if newind < ind:
                        ind = newind
            repodepends.insert(ind,l)
    importedPkgs = set()
    dstring = ''
    for key in stackdepends:
        if key not in importedPkgs:
            importedPkgs.add(key)
            for tup in stackdict[key]:
                dstring = buildImport(key,tup)
                try:
                    exec dstring in globals(), globals()
                    print(dstring)
                except:
                    print('{} did not work.'.format(dstring))
    for key in repodepends:
        if key not in importedPkgs:
            importedPkgs.add(key)
            for tup in repodict[key]:
                dstring = buildImport(key,tup)
                try:
                    exec dstring in globals(), globals()
                    print(dstring)
                except:
                    print('{} did not work.'.format(dstring))
                
def walkDepends(thedict,key,basekeys,importedBy,repodepends,stackdepends,repodict,stackdict):
    for k in thedict[key]['stack']:
        stackdepends.append(k)
        if k not in stackdict:
            stackdict[k] = []
        stackdict[k].extend(thedict[key]['stack'][k])
    for k in thedict[key]['repo']:
        repodepends.append(k)
        if k not in repodict:
            repodict[k] = []
        repodict[k].extend(thedict[key]['repo'][k])
    paths_to_add = set()    
    for k in thedict[key]['repo']:
        if k not in importedBy:
            importedBy[k] = set()
        importedBy[k].add(os.path.basename(key))
        if k != basekeys[k]:
            paths_to_add.add(os.path.dirname(basekeys[k]))
        paths_to_add.update(walkDepends(thedict,basekeys[k],basekeys,importedBy,repodepends,stackdepends,repodict,stackdict))
    return paths_to_add

def buildImport(k,tup):
    if tup[1]:
        return 'from {} import {}'.format(k,','.join(tup[1]))
    elif tup[0]:
        return 'import {} as {}'.format(k,tup[0])
    else:
        return 'import {}'.format(k)

def returnGlobals():
    return globals()
    
if __name__ == '__main__':
#    thefile = 'C://Users/DivollHJ/Documents/Scripts/python/dev/analytix-master/theimports.pkl'
#    buildDepends('Plotterator')
#    scanSource(RELATIVE_LIB_PATH)
    gatherImportsFromRepo(RELATIVE_LIB_PATH)