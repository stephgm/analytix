# -*- coding: utf-8 -*-
"""
Created on Fri Jun 14 13:22:38 2019

@author: DivollHJ
"""
import sys
import os
import cPickle
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
                
def parseImport(line):
    line = line.strip()
    if line.startswith('import'):
        words = line.split()
        if len(words) > 2 and words[2] == 'as':
            return (words[1],words[3],())
        else:
            return (words[1],'',())
    elif line.startswith('from'): # assume from x import y,z,foo
        words = line.split(None,3)
        funcs = map(str.strip,words[3].split(','))
        return (words[1],'',tuple(funcs))
    else:
        return []

def buildDepends(key):
    thedict = cPickle.load(file(os.path.join(os.path.dirname(os.path.realpath(__file__)),'theimports.pkl'),'rb'))
    basekeys = {os.path.basename(k):k for k in thedict}
    basedepends = set(thedict[key])
    paths_to_add = set()
    for l,a,f in thedict[key]:
        if l in basekeys:
            if l != basekeys[l]:
                paths_to_add.add(os.path.dirname(basekeys[l]))
            basedepends.update(thedict[basekeys[l]])
    sys.path.extend([os.path.join(RELATIVE_LIB_PATH,newpath) for newpath in paths_to_add])
    dstring = ''
    for tup in basedepends:
        dstring = buildImport(tup)
        try:
            exec dstring in globals(), globals()
            print(dstring)
        except:
            print('{} did not work.'.format(dstring))
    
def buildImport(tup):
    if tup[2]:
        return 'from {} import {}'.format(tup[0],','.join(tup[2]))
    elif tup[1]:
        return 'import {} as {}'.format(tup[0],tup[1])
    else:
        return 'import {}'.format(tup[0])

def returnGlobals():
    return globals()
    
if __name__ == '__main__':
#    thefile = 'C://Users/DivollHJ/Documents/Scripts/python/dev/analytix-master/theimports.pkl'
    buildDepends('Plotterator')
#    scanSource(RELATIVE_LIB_PATH)