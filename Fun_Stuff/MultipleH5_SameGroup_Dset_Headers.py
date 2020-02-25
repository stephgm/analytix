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


def Open_Multiple_Files_Same_Grp_Dset_Headers(rdir=os.getcwd(),**kwargs):
    '''
    Creates a list widget that will populate the list with available run
    numbers.

    Input:
            rdir - The directory in which you want to start the file searching.
    Kwargs:
        N/A
        
    return:
            Returns a list of concatenated dataframes.
    '''
    title = kwargs.get('title','Select Directory')
    global directory
    basedir = ''
    directory = ''
    nfiles = []
    selection = []
    fpath = ''
    runs = []

    widget = Widgets.QDialog()
    Qt5.loadUi('Multiple_Files_Same_Grps_Dsets_Headers.ui',widget)
    widget.setWindowTitle(title)
    
    def busy():
        Widgets.QApplication.setOverrideCursor(Core.Qt.WaitCursor)
        widget.setEnabled(False)
        Widgets.QApplication.processEvents()
        
    def ready():
        Widgets.QApplication.restoreOverrideCursor()
        widget.setEnabled(True)
        Widgets.QApplication.processEvents()
    
    def reset_widgets():
        widget.filecombo.clear()
        widget.groupcombo.clear()
        widget.runlist.clear()
        widget.dsettabwidget.clear()
    
    def get_directory():
        global directory
        directory = Widgets.QFileDialog.getExistingDirectory(None,'Select A Directory That Contains Runs',rdir,Widgets.QFileDialog.ShowDirsOnly)
        if os.path.isdir(directory):
            reset_widgets()
            widget.directorylabel.setText(directory)
            populate_runs()
        
    def populate_runs():
        global directory
        global runs
        runs = []
        widget.runlist.clear()
        if directory:
            busy()
            if widget.gtruns.isChecked():
                rtype = 'groundtest'
            else:
                rtype = 'other'
            if rtype == 'groundtest':
                runs = glob.glob(os.path.join(directory,'*[0-9].[0-9]'))
                runs = list(map(os.path.basename,runs))
            else:
                runs = [p for p in os.listdir(directory) if os.path.isdir(os.path.join(directory,p))]
            widget.runlist.addItems(runs)
            ready()
            
    def populate_unique_files():
        global directory
        global nfiles
        global basedir
        global selection
        widget.filecombo.clear()
        widget.groupcombo.clear()
        widget.dsettabwidget.clear()
        selection = [str(item.text()) for item in widget.runlist.selectedItems()]
        if directory and selection:
            busy()
            maxlevel = widget.recurselevel.value()
            if maxlevel >= 0:
                maxlevel += 2
            basedir,files = PF.gather_files(directory,ext=['*.h5'],maxDepth=maxlevel)
            nfiles = []
            for file in files:
                for run in selection:
                    if run in file:
                        nfiles.append(file)
            basefiles = list(map(os.path.basename,nfiles))
            unique_files = list(pd.unique(basefiles))
            widget.filecombo.addItems(unique_files)
            ready()
            
    def populate_groups():
        global directory
        global basedir
        global nfiles
        global fpath
        widget.groupcombo.clear()
        widget.dsetlist.clear()
        widget.dsettabwidget.clear()
        if directory and widget.filecombo.currentText():
            busy()
            ctext = widget.filecombo.currentText()
            fpaths = list(map(lambda x: os.path.join(basedir,x),nfiles)) 
            fpath = ''
            for path in fpaths:
                if ctext in os.path.basename(path):
                    fpath = path
                    break
            if fpath and os.path.isfile(fpath):
                grps = PF.get_groups(fpath)
                widget.groupcombo.addItems(grps)
            ready()
            
    def populate_dset_list():
        global directory
        global fpath
        global selection
        widget.dsetlist.clear()
        widget.dsettabwidget.clear()
        if directory and widget.filecombo.currentText() and widget.groupcombo.currentText() and selection:
            if fpath and os.path.isfile(fpath):
                busy()
                grp = widget.groupcombo.currentText()
                dsets = PF.get_dsets(fpath, grp)
                widget.dsetlist.addItems(dsets)
                ready()
            
    def populate_dset_tabs():
        global directory
        global fpath
        global selection
        widget.dsettabwidget.clear()
        if directory and widget.filecombo.currentText() and widget.groupcombo.currentText() and selection:
            if fpath and os.path.isfile(fpath):
                busy()
                grp = widget.groupcombo.currentText()
                dsets = QU.returnListSelection(widget.dsetlist)
                for dset in dsets:
                    listwidget = Widgets.QListWidget()
                    listwidget.setSelectionMode(Widgets.QAbstractItemView.ExtendedSelection)
                    headers = PF.get_headers(fpath, grp, dset)
                    widget.dsettabwidget.addTab(listwidget,f'{dset}')
                    listwidget.addItems(headers)
                ready()
                
    def get_returns():
        global directory
        global fpath
        global selection
        global basedir
        global nfiles
        global runs
        dsetdict={}
        datadict = {}
        rdict = {}
        
        if directory and widget.filecombo.currentText() and widget.groupcombo.currentText() and selection:
            busy()
            fpaths = list(map(lambda x: os.path.join(basedir,x),nfiles))
            cpaths = []
            for path in fpaths:
                if os.path.basename(fpath) in os.path.basename(path):
                    cpaths.append(path)
            grp = widget.groupcombo.currentText()
            for i in range(widget.dsettabwidget.count()):
                lwidget = widget.dsettabwidget.widget(i)
                heads = [str(item.text()) for item in lwidget.selectedItems()]
                if heads:
                    dsetdict[widget.dsettabwidget.tabText(i)] = heads
            
            for key in dsetdict:
                if key not in datadict:
                    datadict[key] = []
                for p in cpaths:
                    run = ''
                    for crun in runs:
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
        ready()
        return rdict
        
    dsetsearch = QU.SearchBar(widget=widget.dsetlist,parent=widget)
    widget.SearchBarLayout.addWidget(dsetsearch)
    
    widget.directorybutton.clicked.connect(lambda:get_directory())
    widget.filecombo.currentIndexChanged.connect(lambda x:populate_groups())
    widget.groupcombo.currentIndexChanged.connect(lambda x:populate_dset_list())
    widget.runlist.itemSelectionChanged.connect(lambda:populate_unique_files())
    widget.dsetlist.itemSelectionChanged.connect(lambda:populate_dset_tabs())
    widget.recurselevel.valueChanged.connect(lambda:populate_unique_files())
    widget.gtruns.toggled.connect(lambda x: populate_runs() if x else False)
    widget.genericruns.toggled.connect(lambda x:populate_runs() if x else False)
    
    
    widget.buttonBox.setStandardButtons(Widgets.QDialogButtonBox.Ok | Widgets.QDialogButtonBox.Cancel)
    widget.buttonBox.accepted.connect(widget.accept)
    widget.buttonBox.rejected.connect(widget.reject)
    ready()
    retval = widget.exec_()

    # 1 is if Ok is pushed... 0 for cancel or 'X'
    if retval == 1:
        return get_returns()
    else:
        return {}
    
    
gg = Open_Multiple_Files_Same_Grp_Dset_Headers('/home/klinetry/Desktop/Phobos3')
print(gg)
