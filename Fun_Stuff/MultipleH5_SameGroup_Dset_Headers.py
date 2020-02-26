#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 24 18:10:13 2020

@author: Carl
"""

import sys
import os

import PyQt5.QtWidgets as Widgets
import PyQt5.QtGui as Gui
import PyQt5.QtCore as Core
import PyQt5.uic as Qt5
import copy
import pandas as pd
import glob
import re
from six import string_types

if not hasattr(sys, 'frozen'):
    RELATIVE_LIB_PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    if __name__ == '__main__':
        sys.path.append(RELATIVE_LIB_PATH)
        sys.path.pop(0)
else:
    RELATIVE_LIB_PATH = os.path.dirname(sys.executable)

RLP = '/home/klinetry/Desktop/Phobos3'
sys.path.append(RLP)

import PhobosFunctions as PF
import QtUtils as QU


class omfsgdh(Widgets.QDialog):
    def __init__(self,parent=None,rdir=os.getcwd(),**kwargs):
        super(omfsgdh,self).__init__(parent)
        Qt5.loadUi('Multiple_Files_Same_Grps_Dsets_Headers.ui',self)
        
        
        title = kwargs.get('title','Select Directory')
        self.setWindowTitle(title)
        
        self.parent = parent
        self.rdir = rdir
        self.directory = ''
        self.nfiles = []
        self.runselection = []
        self.fpath = []
        
        self.makeConnections()
        self.ready()

    def makeConnections(self):
        dsetsearch = QU.SearchBar(widget=self.dsetlist,parent=self)
        self.SearchBarLayout.addWidget(dsetsearch)
        
        self.directorybutton.clicked.connect(lambda:self.get_directory())
        self.gatherfilesbutton.clicked.connect(lambda:self.populate_unique_files())
        self.filecombo.currentIndexChanged.connect(lambda x:self.populate_groups())
        self.groupcombo.currentIndexChanged.connect(lambda x:self.populate_dset_list())
        # widget.runlist.itemSelectionChanged.connect(lambda:populate_unique_files())
        self.runlist.itemSelectionChanged.connect(lambda:self.reset_widgets())
        self.dsetlist.itemSelectionChanged.connect(lambda:self.populate_dset_tabs())
        self.recurselevel.valueChanged.connect(lambda:self.populate_unique_files())
        self.gtruns.toggled.connect(lambda x: self.populate_runs() if x else False)
        self.genericruns.toggled.connect(lambda x:self.populate_runs() if x else False)
        
        
        self.buttonBox.setStandardButtons(Widgets.QDialogButtonBox.Ok | Widgets.QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

    def busy(self):
        Widgets.QApplication.setOverrideCursor(Core.Qt.WaitCursor)
        self.setEnabled(False)
        Widgets.QApplication.processEvents()
        
    def ready(self):
        Widgets.QApplication.restoreOverrideCursor()
        self.setEnabled(True)
        Widgets.QApplication.processEvents()
        
    def reset_widgets(self):
        self.filecombo.clear()
        self.groupcombo.clear()
        self.dsettabwidget.clear()
        
    def get_directory(self):
        directory = Widgets.QFileDialog.getExistingDirectory(self,'Select A Directory That Contains Runs',self.rdir,Widgets.QFileDialog.ShowDirsOnly)
        if os.path.isdir(directory):
            self.directory = directory
            self.reset_widgets()
            self.directorylabel.setText(directory)
            self.populate_runs()
        else:
            self.directory = ''
    
    def populate_runs(self):
        runs = []
        self.runlist.clear()
        if self.directory:
            self.busy()
            if self.gtruns.isChecked():
                rtype = 'groundtest'
            else:
                rtype = 'other'
            if rtype == 'groundtest':
                runs = glob.glob(os.path.join(self.directory,'*[0-9].[0-9]'))
                runs = list(map(os.path.basename,runs))
            else:
                runs = [p for p in os.listdir(self.directory) if os.path.isdir(os.path.join(self.directory,p))]
            self.runlist.addItems(sorted(runs))
            self.ready()
            
    def populate_unique_files(self):
        self.filecombo.clear()
        self.groupcombo.clear()
        self.dsettabwidget.clear()
        self.runselection = QU.returnListSelection(self.runlist)
        if self.directory and self.runselection:
            self.busy()
            maxlevel = self.recurselevel.value()
            if maxlevel >= 0:
                maxlevel += 2
            basedir,files = PF.gather_files(os.path.join(self.directory,self.runselection[0]),ext=['*.h5'],maxDepth=maxlevel)
            self.nfiles = []
            self.filecombo.addItems(files)
            self.ready()
            
    def populate_groups(self):
        self.groupcombo.clear()
        self.dsetlist.clear()
        self.dsettabwidget.clear()
        if self.directory and self.filecombo.currentText():
            self.busy()
            ctext = self.filecombo.currentText()
            self.fpath = os.path.join(self.directory,self.runselection[0],ctext)
            if self.fpath and os.path.isfile(self.fpath):
                grps = PF.get_groups(self.fpath)
                self.groupcombo.addItems(grps)
            self.ready()
            
    def populate_dset_list(self):
        self.dsetlist.clear()
        self.dsettabwidget.clear()
        if self.directory and self.filecombo.currentText() and self.groupcombo.currentText() and self.runselection:
            if self.fpath and os.path.isfile(self.fpath):
                self.busy()
                grp = self.groupcombo.currentText()
                dsets = PF.get_dsets(self.fpath, grp)
                self.dsetlist.addItems(dsets)
                self.ready()
            
    def populate_dset_tabs(self):
        self.dsettabwidget.clear()
        if self.directory and self.filecombo.currentText() and self.groupcombo.currentText() and self.runselection:
            if self.fpath and os.path.isfile(self.fpath):
                self.busy()
                grp = self.groupcombo.currentText()
                dsets = QU.returnListSelection(self.dsetlist)
                for dset in dsets:
                    listwidget = Widgets.QListWidget()
                    listwidget.setSelectionMode(Widgets.QAbstractItemView.ExtendedSelection)
                    headers = PF.get_headers(self.fpath, grp, dset)
                    self.dsettabwidget.addTab(listwidget,f'{dset}')
                    listwidget.addItems(headers)
                self.ready()
                
    def get_returns(self):
        dsetdict={}
        datadict = {}
        rdict = {}
        
        if self.directory and self.filecombo.currentText() and self.groupcombo.currentText() and self.runselection:
            self.busy()
            cpaths = []
            for run in self.runselection:
                base,files = PF.gather_files(os.path.join(self.directory,run),ext=[f'*{os.path.basename(self.fpath)}'])
                cpaths += list(map(lambda x:os.path.join(base,x),files))
            grp = self.groupcombo.currentText()
            for i in range(self.dsettabwidget.count()):
                lwidget = self.dsettabwidget.widget(i)
                heads = [str(item.text()) for item in lwidget.selectedItems()]
                if heads:
                    dsetdict[self.dsettabwidget.tabText(i)] = heads
            
            for key in dsetdict:
                if key not in datadict:
                    datadict[key] = []
                for p in cpaths:
                    run = ''
                    for crun in self.runselection:
                        if crun in p:
                            run = crun
                            break
                        else:
                            run = ''
                    datadict[key].append(PF.get_h5_data(p, grp, key, headers=datadict[key],addCustom={'Run':run}))
            
            for key in datadict:
                if len(datadict[key]) > 1:
                    rdict[key] = datadict[key][0].append(datadict[key][1:],ignore_index=True)
                elif len(datadict[key]) == 1:
                    rdict[key] = datadict[key][0]
                elif len(datadict[key]) == 0:
                    rdict[key] = []
        self.ready()
        return rdict
    
def open_the_stuff(parent=None,rdir=os.getcwd(),**kwargs):
    xx = omfsgdh(parent,rdir,**kwargs)
    retval = xx.exec_()
    if retval == 1:
        return xx.get_returns()
    else:
        return {}
    
# gg = Open_Multiple_Files_Same_Grp_Dset_Headers('/home/klinetry/Desktop/Phobos3')
gg = open_the_stuff(None,'/home/klinetry/Desktop/Phobos3',title='What')
print(gg)
