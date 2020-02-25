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
    widget.setWindowTitle(title)
    buttonBox = Widgets.QDialogButtonBox(widget)
    layout = Widgets.QGridLayout()
    
    def busy():
        Widgets.QApplication.setOverrideCursor(Core.Qt.WaitCursor)
        widget.setEnabled(False)
        Widgets.QApplication.processEvents()
        
    def ready():
        Widgets.QApplication.restoreOverrideCursor()
        widget.setEnabled(True)
        Widgets.QApplication.processEvents()
    
    def reset_widgets():
        filecombo.clear()
        groupcombo.clear()
        runlist.clear()
        dsettabwidget.clear()
    
    def get_directory():
        global directory
        directory = Widgets.QFileDialog.getExistingDirectory(None,'Select A Directory',rdir,Widgets.QFileDialog.ShowDirsOnly)
        if os.path.isdir(directory):
            reset_widgets()
            directorylabel.setText(directory)
            populate_runs()
        
    def populate_runs():
        global directory
        global runs
        runs = []
        runlist.clear()
        if directory:
            busy()
            if gtruns.isChecked():
                rtype = 'groundtest'
            else:
                rtype = 'other'
            if rtype == 'groundtest':
                runs = glob.glob(os.path.join(directory,'*[0-9].[0-9]'))
                runs = list(map(os.path.basename,runs))
            else:
                runs = [p for p in os.listdir(directory) if os.path.isdir(os.path.join(directory,p))]
            runlist.addItems(runs)
            ready()
            
    def populate_unique_files():
        global directory
        global nfiles
        global basedir
        global selection
        filecombo.clear()
        groupcombo.clear()
        dsettabwidget.clear()
        selection = [str(item.text()) for item in runlist.selectedItems()]
        if directory and selection:
            busy()
            maxlevel = recurselevel.value()
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
            filecombo.addItems(unique_files)
            ready()
            
    def populate_groups():
        global directory
        global basedir
        global nfiles
        global fpath
        groupcombo.clear()
        dsetlist.clear()
        dsettabwidget.clear()
        if directory and filecombo.currentText():
            busy()
            ctext = filecombo.currentText()
            fpaths = list(map(lambda x: os.path.join(basedir,x),nfiles)) 
            fpath = ''
            for path in fpaths:
                if ctext in os.path.basename(path):
                    fpath = path
                    break
            if fpath and os.path.isfile(fpath):
                grps = PF.get_groups(fpath)
                groupcombo.addItems(grps)
            ready()
            
    def populate_dset_list():
        global directory
        global fpath
        global selection
        dsetlist.clear()
        dsettabwidget.clear()
        if directory and filecombo.currentText() and groupcombo.currentText() and selection:
            if fpath and os.path.isfile(fpath):
                busy()
                grp = groupcombo.currentText()
                dsets = PF.get_dsets(fpath, grp)
                dsetlist.addItems(dsets)
                ready()
            
    def populate_dset_tabs():
        global directory
        global fpath
        global selection
        dsettabwidget.clear()
        if directory and filecombo.currentText() and groupcombo.currentText() and selection:
            if fpath and os.path.isfile(fpath):
                busy()
                grp = groupcombo.currentText()
                dsets = QU.returnListSelection(dsetlist)
                for dset in dsets:
                    listwidget = Widgets.QListWidget()
                    listwidget.setSelectionMode(Widgets.QAbstractItemView.ExtendedSelection)
                    headers = PF.get_headers(fpath, grp, dset)
                    dsettabwidget.addTab(listwidget,f'{dset}')
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
        
        if directory and filecombo.currentText() and groupcombo.currentText() and selection:
            busy()
            fpaths = list(map(lambda x: os.path.join(basedir,x),nfiles))
            cpaths = []
            for path in fpaths:
                if os.path.basename(fpath) in os.path.basename(path):
                    cpaths.append(path)
            grp = groupcombo.currentText()
            for i in range(dsettabwidget.count()):
                widget = dsettabwidget.widget(i)
                heads = [str(item.text()) for item in widget.selectedItems()]
                if heads:
                    dsetdict[dsettabwidget.tabText(i)] = heads
            
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
        
    
    directorybutton = Widgets.QPushButton('Select Directory')
    directorybutton.clicked.connect(lambda:get_directory())
    
    directorylabel = Widgets.QLabel()
    
    filelabel = Widgets.QLabel('File Selection')
    
    filecombo = Widgets.QComboBox()
    filecombo.currentIndexChanged.connect(lambda x:populate_groups())
    
    grouplabel = Widgets.QLabel('Group Selection')
    
    groupcombo = Widgets.QComboBox()
    groupcombo.currentIndexChanged.connect(lambda x:populate_dset_list())
    
    runlist = Widgets.QListWidget()
    runlist.setSelectionMode(Widgets.QAbstractItemView.ExtendedSelection)
    runlist.itemSelectionChanged.connect(lambda:populate_unique_files())
    
    findfilesbutton = Widgets.QPushButton('Find Files')
    findfilesbutton.clicked.connect(populate_unique_files)
    
    dsetlistlabel = Widgets.QLabel('Select Dsets to Show')
    dsetlist = Widgets.QListWidget()
    dsetlist.setSelectionMode(Widgets.QAbstractItemView.ExtendedSelection)
    dsetlist.itemSelectionChanged.connect(lambda:populate_dset_tabs())
    
    dsetsearch = QU.SearchBar(widget=dsetlist,parent=widget)
    
    dsetlabel = Widgets.QLabel('Dset Tabs')
    
    recurselabel = Widgets.QLabel('Search Depth')
    recurselevel = Widgets.QSpinBox()
    recurselevel.setMinimum(-1)
    recurselevel.setMaximum(99)
    recurselevel.setValue(-1)
    recurselevel.valueChanged.connect(lambda:populate_unique_files())
    
    rungroup = Widgets.QGroupBox()
    rungrouplabel = Widgets.QLabel('Run Selection Type')
    gtruns = Widgets.QRadioButton('Ground Test')
    gtruns.setChecked(True)
    gtruns.toggled.connect(lambda x: populate_runs() if x else False)
    genericruns = Widgets.QRadioButton('Generic')
    genericruns.toggled.connect(lambda x:populate_runs() if x else False)
    grouplayout = Widgets.QGridLayout()
    grouplayout.addWidget(rungrouplabel,0,0,1,2)
    grouplayout.addWidget(gtruns,1,0)
    grouplayout.addWidget(genericruns,1,1)
    rungroup.setLayout(grouplayout)
    
    
    dsettabwidget = Widgets.QTabWidget()
    dsettabwidget.setMinimumSize(Core.QSize(400,100))
    
    layout.addWidget(rungroup,0,0,1,2)
    layout.addWidget(recurselabel,1,0)
    layout.addWidget(recurselevel,1,1)
    layout.addWidget(directorybutton,2,0)
    layout.addWidget(directorylabel,2,1)
    layout.addWidget(runlist,3,0,1,2)
    layout.addWidget(findfilesbutton,4,0,1,2)
    layout.addWidget(filelabel,5,0)
    layout.addWidget(filecombo,5,1)
    layout.addWidget(grouplabel,6,0)
    layout.addWidget(groupcombo,6,1)
    layout.addWidget(dsetlistlabel,7,0,1,2)
    layout.addWidget(dsetsearch,8,0,1,2)
    layout.addWidget(dsetlist,9,0,1,2)
    layout.addWidget(dsetlabel,10,0,1,2)
    layout.addWidget(dsettabwidget,11,0,1,2)
    layout.addWidget(buttonBox)
    
    widget.setLayout(layout)
    
    
    buttonBox.setStandardButtons(Widgets.QDialogButtonBox.Ok | Widgets.QDialogButtonBox.Cancel)
    buttonBox.accepted.connect(widget.accept)
    buttonBox.rejected.connect(widget.reject)
    ready()
    retval = widget.exec_()

    # 1 is if Ok is pushed... 0 for cancel or 'X'
    if retval == 1:
        return get_returns()
    else:
        return {}
    
    
gg = Open_Multiple_Files_Same_Grp_Dset_Headers('/home/klinetry/Desktop/Phobos3')
