# -*- coding: utf-8 -*-
"""
Created on Fri Jul 12 18:20:43 2019

@author: Jordan Muffukin Marlow
"""

##FOR THE LOVE OF GOD, PUT THIS FILE IN AN ISOLATED PLACE... IT WILL DELETE EMPTY FOLDERS
#But I put logic in

#If you are interested in where the structure came from:
# http://classic.battle.net/diablo2exp/items/runewords-original.shtml
#These are runewords from an old game I use to play.  This makes it more
#tangible for myself.  The website can also be used as a sort of guide of what will import what.

import os

#To lazy to just not make the folders that have nothing in them..
def removeEmptyFolders(path, removeRoot=True):
  'Function to remove empty folders'
  if not os.path.isdir(path):
    return

  # remove empty subfolders
  files = os.listdir(path)
  if len(files):
    for f in files:
      fullpath = os.path.join(path, f)
      if os.path.isdir(fullpath):
        removeEmptyFolders(fullpath)

  # if folder empty, delete it
  files = os.listdir(path)
  if len(files) == 0 and removeRoot:
    print "Removing empty folder:", path
    os.rmdir(path)

dictoRunewords109 = dict(AncientsPledge=['Ral','Ort','Tal'],\
                      Black = ['Thul','Io','Nef'],\
                      Fury = ['Jah','Gul','Eth'],\
                      HolyThunder=['Eth','Ral','Ort','Tal'],\
                      Honor=['Amn','El','Ith','Tir','Sol'],\
                      KingsGrace=['Amn','Ral','Thul'],\
                      Leaf=['Tir','Ral'],\
                      Lionheart=['Hel','Lum','Fal'],\
                      Lore=['Ort','Sol'],\
                      Malice=['Ith','El','Eth'],\
                      Melody=['Shael','Ko','Nef'],\
                      Memory=['Lum','Io','Sol','Eth'],\
                      Nadir=['Nef','Tir'],\
                      Radiance=['Nef','Sol','Ith'],\
                      Rhyme=['Shael','Eth'],\
                      Silence=['Dol','Eld','Hel','Ist','Tir','Vex'],\
                      Smoke=['Nef','Lum'],\
                      Stealth=['Tal','Eth'],\
                      Steel=['Tir','El'],\
                      Strength=['Amn','Tir'],\
                      Venom=['Tal','Dol','Mal'],\
                      Wealth=['Lem','Ko','Tir'],\
                      White=['Dol','Io'],\
                      Zephyr=['Ort','Eth'])

repodir = os.path.dirname(os.path.realpath(__file__))

answer = raw_input("This script will delete any empty folders in "+repodir+"\nDo you want to continue? (y/n): ")
if str(answer).lower() == 'y':

    for runeword in dictoRunewords109:
        if os.path.isdir(os.path.join(repodir,runeword)):
            pass
        else:
            os.mkdir(os.path.join(repodir,runeword))
            pass
        for rune in dictoRunewords109[runeword]:
            dontmake = False
            for key in dictoRunewords109:
                if os.path.isfile(os.path.join(repodir,key,rune+'.py')):
                    dontmake = True
                    break
            if not dontmake:
                fid = file(os.path.join(repodir,runeword,rune+'.py'),'wb')
                fid.write('import os\n')
                fid.write('import sys\n')
                fid.write('import glob\n')
                fid.write('REL_LIB_PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))\n')
                fid.write('sys.path.extend(glob.glob(os.path.join(REL_LIB_PATH,"*")))\n')
                imports = ['import {}\n'.format(x) for x in dictoRunewords109[runeword] if x != rune]
                fid.writelines(imports)
                somedef = 'def fingeritout{}(): print "{} in {}"'.format(rune,rune,runeword)
                fid.write(somedef)
                fid.close()
        removeEmptyFolders(repodir)
    print("Hope you knew what you were doing.")
else:
    print('You just avoided disaster.... Good call.  Go have a beer to calm down.')
                
