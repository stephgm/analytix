#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 18 21:27:11 2019

@author: Jordan
"""

import PyQt5.QtWidgets as Widgets
import PyQt5.QtGui as Gui
import PyQt5.QtCore as Core
from PyQt5 import uic

import os
import sys
import multiprocessing
from collections import OrderedDict, Iterable
import pandas as pd
import copy
import time
import uuid

import QtUtils
import PhobosFunctions
import GeneralFilter


EventDict = {'home':['056.1','092.1']}

def stupid():
    print 'FUNNNN'

class ProgressIndicator(Widgets.QWidget):
    def __init__(self,label,tid,parent=None):
        super(ProgressIndicator,self).__init__(parent)
        self.parent = parent
        self.label = label
        self.tid = tid
        self.layout = Widgets.QGridLayout()
        self.ProcessLabel = Widgets.QLabel(self.label)
        self.ColorLine = Widgets.QLineEdit()
        self.ColorLine.setReadOnly(True)

        self.setLayout(self.layout)
        self.layout.addWidget(self.ProcessLabel,0,0)
        self.layout.addWidget(self.ColorLine,0,1)

class ProgressIndicatorUpdater(Core.QThread):
    UpdateColor = Core.pyqtSignal(object)
    Stopped = Core.pyqtSignal(object)
    def __init__(self,layout,parent=None):
        super(ProgressIndicatorUpdater,self).__init__(parent)
        self.parent = parent
        self.layout = layout
        self.running = True
        self.initWidget()

    def initWidget(self):
        self.widget = ProgressIndicator('This Thang',self.getThreadId())
        self.layout.addWidget(self.widget)

    def getThreadId(self):
        return id(self)

    def run(self):
        i = 0
        while self.running:
            i += 25
            if i > 254:
                i = 0
            palette = Gui.QPalette()
            color = Gui.QColor(i,254,0)
            palette.setColor(self.widget.ColorLine.backgroundRole(),color)
            self.widget.ColorLine.setAutoFillBackground(True)
            self.widget.ColorLine.setPalette(palette)
            time.sleep(.3)

    def stop(self):
        self.widget.deleteLater()
        self.running = False
        time.sleep(.1)
        self.Stopped.emit(self.getThreadId())

class AddNativeHeadersWidget(Widgets.QWidget):
    Selection = Core.pyqtSignal(object)
    def __init__(self,headers,parent=None,**kwargs):
        super(AddNativeHeadersWidget,self).__init__(parent)
        self.parent = parent
        self.headers = headers

        self.makeWidget()

    def makeWidget(self):
        self.layout = Widgets.QGridLayout()
        self.setLayout(self.layout)
        self.HeaderListWidget = Widgets.QListWidget()
        self.HeaderListWidget.addItems(self.headers)
        self.SearchBar = QtUtils.SearchBar(self.HeaderListWidget,self,regex=False)
        self.AddButton = Widgets.QPushButton('Add Selected')
        self.AddButton.clicked.connect(lambda:self.addSelected())
        self.layout.addWidget(self.SearchBar,0,0)
        self.layout.addWidget(self.HeaderListWidget,1,0)
        self.layout.addWidget(self.AddButton,2,0)

    def setList(self,headers):
        self.HeaderListWidget.clear()
        self.headers = copy.copy(headers)
        self.HeaderListWidget.addItems(self.headers)

    def addSelected(self):
        selectedHeaders = returnListSelection(self.HeaderListWidget)
        if selectedHeaders:
            self.Selection.emit(selectedHeaders)

class StatTable(Widgets.QDockWidget):
    Closing = Core.pyqtSignal(bool)
    def __init__(self,parent,**kwargs):
        super(StatTable,self).__init__(parent)
        self.parent = parent
        self.setFixedHeight(325)
        self.setAttribute(Core.Qt.WA_DeleteOnClose, True)

        self.makeWidget()

    def makeWidget(self):
        self.Table = Widgets.QTableView()
        self.setWidget(self.Table)

    def calcStats(self,data):
        features = ['# of Unique Vals','Max','25%','50%','75%','Min','Mean','Std. Dev.','Most Frequent']
        statdat = pd.DataFrame(index=features,columns=list(data))
        for header in list(data):
            statdat[header].iloc[0] = len(pd.unique(data[header]))
            if data[header].dtype.kind not in ['O','b']:
                statdat[header].iloc[1] = data[header].max()
                statdat[header].iloc[2] = data[header].quantile(.25)
                statdat[header].iloc[3] = data[header].quantile(.5)
                statdat[header].iloc[4] = data[header].quantile(.75)
                statdat[header].iloc[5] = data[header].min()
                statdat[header].iloc[6] = data[header].mean()
                statdat[header].iloc[7] = data[header].std()
            else:
                statdat[header].iloc[1] = 'N/A'
                statdat[header].iloc[2] = 'N/A'
                statdat[header].iloc[3] = 'N/A'
                statdat[header].iloc[4] = 'N/A'
                statdat[header].iloc[5] = 'N/A'
                statdat[header].iloc[6] = 'N/A'
                statdat[header].iloc[7] = 'N/A'
            statdat[header].iloc[8] = data[header].astype(str).value_counts().idxmax()
        self.model = PhobosTableModel(statdat,self,rowLabels=features)
        self.Table.setModel(self.model)

    def closeEvent(self,event):
        self.Closing.emit(True)
        event.accept()

class TabTableWidget(Widgets.QWidget):
    AddableChanged = Core.pyqtSignal(object)
    def __init__(self,parent=None,data=None,**kwargs):
        super(TabTableWidget,self).__init__(parent)
        self.parent = parent
        self.StatTable = None
        #Items that will keep the attributes of each TabTableWidget
        #Keep a list of file paths to get data from addNativeHeaders
        #The order of these lists matter when it comes to concatenation
        self.fpaths = kwargs.get('fpaths',[])
        self.groups = kwargs.get('groups',[])
        self.dsets = kwargs.get('dsets',[])
        self.nativeheaders = kwargs.get('native',[])
        self.addedHeaders = kwargs.get('added',pd.DataFrame())
        self.currentHeaders = []
        self.runs = []
        self.events = []
        self.filters = []

        self.getEventandRun()
#        self.proxySortFilt = PhobosTableModelProxyFilter(self).setModel(self.model)
        self.makeWidget()
        self.makeConnections()

        self.model = PhobosTableModel(data,self.nativeheaders,self.Table)
        self.numRows = self.model.rowCount()
        self.currentHeaders = self.model.getHeaderNames()
        self.updateCurrentHeaders()

    def makeConnections(self):
        self.ShowStatChk.toggled.connect(self.showStatTable)
        self.model.DataChanged.connect(lambda:self.updateStatTable())
        self.model.RowChanged.connect(lambda:self.getRowNum())
        self.model.ColumnChanged.connect(lambda:self.updateCurrentHeaders())

    def makeWidget(self):
        self.layout = Widgets.QGridLayout()
        self.IdLabel = Widgets.QLabel(str(self.fpaths))
        self.NumRowWidget = Widgets.QWidget()
        self.NumRowLayout = Widgets.QHBoxLayout()
        self.NumRowWidget.setLayout(self.NumRowLayout)
        self.NumRowLabel = Widgets.QLabel('Number of Rows')
        self.NumRow = Widgets.QLabel(str(self.numRows))
        self.NumRowSpacer = Widgets.QSpacerItem(10,10 , Widgets.QSizePolicy.Expanding, Widgets.QSizePolicy.Minimum)
        self.NumRowLayout.addWidget(self.NumRowLabel)
        self.NumRowLayout.addWidget(self.NumRow)
        self.NumRowLayout.addItem(self.NumRowSpacer)
        self.ShowStatChk = Widgets.QCheckBox()
        self.ShowStatChk.setText('Show Statistics')
        self.Table = Widgets.QTableView()
        self.Table.setModel(self.model)
        self.layout.addWidget(self.IdLabel,0,0)
        self.layout.addWidget(self.NumRowWidget,1,0)
        self.layout.addWidget(self.ShowStatChk,2,0)
        self.layout.addWidget(self.Table,3,0)
        self.setLayout(self.layout)
        self.hheaders = self.Table.horizontalHeader()
        self.hheaders.setContextMenuPolicy(Core.Qt.CustomContextMenu)
        self.hheaders.customContextMenuRequested.connect(self.table_header_context)
        self.vheaders = self.Table.verticalHeader()
        self.vheaders.setContextMenuPolicy(Core.Qt.CustomContextMenu)
        self.vheaders.customContextMenuRequested.connect(self.table_row_context)

    def setModel(self,model):
        self.model = model
        self.Table.setModel(self.model)
        self.getRowNum()
        self.currentHeaders = self.model.getHeaderNames()
        self.model.DataChanged.connect(lambda:self.updateStatTable())
        self.model.RowChanged.connect(lambda:self.getRowNum())
        self.model.ColumnChanged.connect(lambda:self.updateCurrentHeaders())

    def getRowNum(self):
        self.numRows = self.model.rowCount(self)
        self.NumRow.setText(str(self.numRows))

    def updateCurrentHeaders(self):
        removed = set(self.currentHeaders) - set(self.model.getHeaderNames())
        added = set(self.model.getHeaderNames()) - set(self.currentHeaders)
        if added:
            for new in added:
                if new not in self.nativeheaders:
                    self.addedHeaders[new] = self.model.getColumnData(new)
        if removed:
            self.addedHeaders.drop([header for header in removed if header in self.addedHeaders])
        self.currentHeaders = self.model.getHeaderNames()
        self.addableHeaders = set(self.nativeheaders) - set(self.currentHeaders)
        self.AddableChanged.emit(self.addableHeaders)


    def showStatTable(self,show):
        if show:
            self.StatTable = StatTable(self)
            self.layout.addWidget(self.StatTable)
            self.StatTable.calcStats(self.model.getTableData())
            self.StatTable.Closing.connect(lambda check:self.ShowStatChk.setChecked(False))
        else:
            self.StatTable.deleteLater()
            self.StatTable = None

    def updateStatTable(self):
        print 'in hereeee'
        if self.StatTable:
            print 'in here'
            self.StatTable.calcStats(self.model.getTableData())

    def table_header_context(self,pos,**kwargs):
        menu = Widgets.QMenu(self)
        menu.addAction('stuff')
        menu.addAction("Segunda opción")
        menu.addAction(":)")
        menu.exec_(Gui.QCursor.pos())

    def table_row_context(self,pos,**kwargs):
        menu = Widgets.QMenu(self)
        HideRows = menu.addAction('Hide Row(s)')
        action = menu.exec_(self.Table.mapToGlobal(pos))
        if action == HideRows:
            selected = QtUtils.returnTableSelectedRows(self.Table)
            if selected:
                self.model.hideRows(selected)

    def getEventandRun(self):
        for path in self.fpaths:
            splitpath = path.split(os.sep)
            for event,runs in EventDict.iteritems():
                if event in splitpath:
                    self.events.append(event)
                    for run in runs:
                        if run in splitpath:
                            self.runs.append(run)
                            break
                    break
        print self.events
        print self.runs


class RetrieveData(Core.QThread):
    EmitRetrievedData = Core.pyqtSignal(object,object)
    QueryFinished = Core.pyqtSignal(object)
    StatusPartner = Core.pyqtSignal(object)
    def __init__(self,target,args=(),kwargs={},parent=None):
        super(RetrieveData,self).__init__(parent)
        self.target = target
        self.args = args
        self.kwargs = kwargs

        self.statusTID = None

    def getThreadId(self):
        return id(self)

    def run(self):
        data = self.target(*self.args,**self.kwargs)
        self.EmitRetrievedData.emit(data,list(data))
        self.QueryFinished.emit(self.getThreadId())
        self.StatusPartner.emit(self.statusTID)

class FileSearchSelector(Widgets.QWidget):
    buttonChanged = Core.pyqtSignal(object)
    def __init__(self,parent=None,**kwargs):
        super(FileSearchSelector,self).__init__(parent)
        self.parent = parent
        self.layout = Widgets.QGridLayout()
        self.setLayout(self.layout)
        group = self.makeGroup()
        self.layout.addWidget(group,0,0)

        self.makeConnections()

    def makeConnections(self):
        self.File.toggled.connect(lambda trash:self.Emit())
        self.Group.toggled.connect(lambda trash:self.Emit())
        self.Dset.toggled.connect(lambda trash:self.Emit())
        self.Header.toggled.connect(lambda trash:self.Emit())

    def Emit(self):
        if self.File.isChecked():
            self.buttonChanged.emit('File')
        elif self.Group.isChecked():
            self.buttonChanged.emit('Group')
        elif self.Dset.isChecked():
            self.buttonChanged.emit('Dset')
        elif self.Header.isChecked():
            self.buttonChanged.emit('Header')

    def makeGroup(self):
        group = Widgets.QGroupBox()
        grouplayout = Widgets.QGridLayout()
        self.Label = Widgets.QLabel('Select Search')
        self.Label.setSizePolicy(Widgets.QSizePolicy.Expanding, Widgets.QSizePolicy.Expanding)
        self.Label.setAlignment(Core.Qt.AlignCenter)
        self.File = Widgets.QRadioButton('File')
        self.Group = Widgets.QRadioButton('Group')
        self.Dset = Widgets.QRadioButton('Dataset')
        self.Header = Widgets.QRadioButton('Header')
        grouplayout.addWidget(self.Label,0,1,1,2)
        grouplayout.addWidget(self.File,1,0)
        grouplayout.addWidget(self.Group,1,1)
        grouplayout.addWidget(self.Dset,1,2)
        grouplayout.addWidget(self.Header,1,3)
        group.setLayout(grouplayout)
        self.File.setChecked(True)
        return group

class PhobosTableModel(Core.QAbstractTableModel):
    DataChanged = Core.pyqtSignal()
    ColumnChanged = Core.pyqtSignal()
    RowChanged = Core.pyqtSignal()
    def __init__(self, datain=pd.DataFrame(),nativeheaders = [], parent=None,**kwargs):
        Core.QAbstractTableModel.__init__(self, parent)
        self.parent = parent
        self.edit = kwargs.get('editable',False)
        self.rowLabels = kwargs.get('rowLabels',None)
        if not isinstance(self.edit,bool):
            self.edit = False
        if not isinstance(datain,pd.DataFrame):
            print('The data passed to Phobos table model is not a DataFrame.  Trying to convert')
            try:
                datain = pd.DataFrame(datain)
                print('Conversion successful, but change that in your code')
            except:
                print('Conversion unsuccessful, making empty DataFrame.')
                datain = pd.DataFrame()
        if nativeheaders:
            self.NativeHeaders = copy.copy(nativeheaders)
        else:
            self.NativeHeaders = list(datain)
        if self.edit:
            self.editHeader = 'Table Edited'
            datain[self.editHeader] = pd.Series([0]*datain.shape[0])

        self.FilterIdx = pd.Series([True]*datain.shape[0])

        self.arraydata = copy.deepcopy(datain)
        #Need to figure out how to stop copying the datain a 2nd time.. gonna look into sortfilterproxymodel
        self.origdata = copy.deepcopy(datain)

    def handleValue(self,header,value):
        if header in self.arraydata:
            dtype = self.arraydata[header].dtype.kind
            if dtype in ['u','i']:
                try:
                    value = int(value)
                except:
                    return None
            elif dtype in ['b']:
                try:
                    value = value == 'True'
                except:
                    return None
            elif dtype in ['f']:
                try:
                    value = float(value)
                except:
                    return None
        return value

    def rowCount(self, parent=None):
        return self.arraydata.shape[0]

    def columnCount(self, parent=None):
        return self.arraydata.shape[1]

    def headerData(self, section, orientation = Core.Qt.Horizontal, role=Core.Qt.DisplayRole):
        if role == Core.Qt.DisplayRole:
            if orientation == Core.Qt.Horizontal:
                return list(self.arraydata)[section]
            elif orientation == Core.Qt.Vertical:
                return str(self.arraydata.index[section])
            else:
                return section

    def flags(self, index):
        if list(self.arraydata)[index.column()] not in self.NativeHeaders:
                return Core.Qt.ItemIsEnabled | Core.Qt.ItemIsEditable | Core.Qt.ItemIsSelectable
        elif self.edit:
            if list(self.arraydata)[index.column()] != self.editHeader:
                return Core.Qt.ItemIsEnabled | Core.Qt.ItemIsEditable | Core.Qt.ItemIsSelectable

        return Core.Qt.ItemIsEnabled | Core.Qt.ItemIsSelectable

    def data(self, index, role):
        if not index.isValid():
            return None
        if role == Core.Qt.DisplayRole:
            if list(self.arraydata)[index.column()] in self.arraydata:
                value = self.arraydata[list(self.arraydata)[index.column()]].iat[index.row()]
            else:
                value = ''
            return str(value)
### Get Data

    def getTableData(self):
        return self.arraydata

    def getHeaderNames(self):
        return list(self.arraydata)

    def getColumnData(self,header):
        if header in list(self.arraydata):
            return self.arraydata[header]

    def getOrigData(self):
        return self.origdata

    def getSaveData(self):
        return self.origdata[self.NativeHeaders]

### Add Data

    def addColumnData(self,data):
        headers = list(data)
        addlist = []
        for header in headers:
            if header not in list(self.arraydata):
                addlist.append(header)
        if addlist:
            #This is for when I no longer have to pair down arraydata for filtering
#            self.arraydata = self.arraydata.join(data[addlist])
            self.origdata = self.origdata.join(data[addlist])
            print list(self.origdata)
            self.updateTableData()
            self.updateColumns()

### Remove Data

    def removeColumns(self,headers):
        removelist = []
        for header in headers:
            if header in list(self.arraydata):
                removelist.append(header)
        if removelist:
#            self.arraydata.drop(removelist,axis=1)
            self.origdata.drop(removelist,axis=1)
            self.updateTableData()
            self.updateColumns()

### Data Changing

    def updateCell(self):
        self.DataChanged.emit()
        self.layoutChanged.emit()

    def updateColumns(self):
        self.ColumnChanged.emit()
        self.DataChanged.emit()
        self.layoutChanged.emit()

    def updateRows(self):
        self.RowChanged.emit()
        self.DataChanged.emit()
        self.layoutChanged.emit()

    def updateTableData(self):
        self.origdata = self.origdata.reindex(self.FilterIdx.index)
        self.arraydata = copy.deepcopy(self.origdata[self.FilterIdx])
        self.dataChanged.emit(self.createIndex(0, 0), self.createIndex(self.rowCount(0), self.columnCount(0)))
        self.layoutChanged.emit()

    def setData(self, index, value, role):
        if role == Core.Qt.EditRole:
            row = index.row()
            column = index.column()
            dtype = self.arraydata[list(self.arraydata)[column]].dtype.kind
            value = self.handleValue(list(self.arraydata)[column],value)
            if value == None:
                return False
            print row
            self.arraydata[list(self.arraydata)[column]].iat[row] = value
            if self.edit:
                if value == self.origdata[list(self.arraydata)[column]].iat[row]:
                    self.arraydata[self.editHeader].iat[row] = 0
                    self.origdata[self.editHeader].iat[row] = 0
                else:
                    self.arraydata[self.editHeader].iat[row] = 1
                    self.origdata[self.editHeader].iat[row] = 1
            self.dataChanged.emit(index, index)
            self.updateCell()
            return True
        else:
            return False

    def setCellValue(self,header,row,value):
        if header in list(self.arraydata):
            if row in self.arraydata[header].index:
                value = self.handleValue(header,value)
                if value == None:
                    print('Value entered could not be interpreted')
                else:
                    self.arraydata[header].iat[row] = value
                    self.origdata[header].iat[row] = value
                    self.updateCell()
            else:
                print('row was not in table!')
        else:
            print('{} was not in table headers'.format(header))

    def filterTable(self,procedures):
        self.FilterIdx = GeneralFilter.generalFilter(self.origdata,[['inSearchPlan','Ascending Order','','','']],getidx=True)
        self.updateTableData()
        self.updateRows()

class PhobosTableModelProxyFilter(Core.QSortFilterProxyModel):
    def __init__(self,parent=None,**kwargs):
        super(PhobosTableModelProxyFilter,self).__init(parent)


class Phobos(Widgets.QMainWindow):
    def __init__(self,parent=None,**kwargs):
        super(Phobos,self).__init__(parent)
        uic.loadUi('PyqtTest.ui', self)
        #Essential Variables on startup that do not need to be reset when making a 'New Project'
        self.parent = parent
        self.threads = {}
        self.numcores = multiprocessing.cpu_count()
        self.LastDirectory = os.getcwd()
        self.DataFileExtensions = OrderedDict()
        self.DataFileExtensions['HDF5 File'] = ['.h5']
#        self.DataFileExtensions['CSV File'] = ['.csv']
        self.DataFileExtensions['Excel File'] = ['.xlsx']
        self.DataFileExtensions['Pickle File'] = ['.pkl']

        # Function Overrides.  Usually from QtUtils.py
        self.Alert = QtUtils.Alert
        self.dragEnterEvent = QtUtils.dragEnterEvents

        #Gui Properties to set up on init
        self.setAcceptDrops(True)
        self.fileSearcher = FileSearchSelector(self)
        self.searchBar = QtUtils.SearchBar(self.FileNameCombo,self)
        self.SearchQWidgetLayout.addWidget(self.fileSearcher)
        self.SearchQWidgetLayout.addWidget(self.searchBar)
        self.AddNativeHeader = AddNativeHeadersWidget([],self)
        self.NativeHeaderLayout.addWidget(self.AddNativeHeader)
        self.FileOpenStackedSplitter.setSizes((200,10000))
        self.setupToolbar()
        #Init variables that need to be reset on 'New Project'
        self.initialize()

        '''
        Kwargs descriptions
            throttle -  Gets the number of cores on the system being ran,
                        Will not let the user use create more threads within
                        this process than are available on their machine.
                        That is, unless they choose to continue anyways.
                        If a status indicator is used while something is being
                        threaded, then it will generate 2 threads instead
                        of 1.  This is because I need 1 thread to get data and
                        another thread to show an indicator that the Gui is
                        doing something per everyone's want.

        '''
        #Kwargs Only
        self.throttle = kwargs.get('throttle',True)

        #Make all signal slot connections for the GUI.  All data getting signals
        #are handled elsewhere because they need to be created on thread creation
        self.makeConnections()

    def initialize(self):
        #This function is for variables that need to be set/reset on
        #open/new project.
        self.tableDict = {}
        pass

    def makeConnections(self):
        #This is where all GUI Widget signals and slots are stored
        self.Button1.clicked.connect(lambda:self.scan_directory())
        self.GetSelection.clicked.connect(lambda:self.filterTable())
        self.CreateTable.clicked.connect(lambda:self.get_data_from_file())
        self.CreateTable.clicked.connect(lambda:self.GatherPct.setText('100'))


        self.fileSearcher.buttonChanged.connect(self.setSearchWidget)
        self.AddNativeHeader.Selection.connect(self.addNativeHeaders)

        self.FileNameCombo.currentIndexChanged.connect(lambda:self.populate_groups())
        self.GroupNameCombo.currentIndexChanged.connect(lambda:self.populate_datasets())
        self.DatasetList.itemSelectionChanged.connect(lambda:self.populate_headers())

### Core Gui Functions

    def setupToolbar(self):
        resourcedir = os.path.join(os.getcwd(),'resources')
        opensinglefile = Widgets.QAction(Gui.QIcon(os.path.join(resourcedir,'open_file.png')),'Open Single File',self)
        opensinglefile.triggered.connect(self.get_single_filename)
        openmultifiles = Widgets.QAction(Gui.QIcon(os.path.join(resourcedir,'open_files.png')),'Open Multiple Files',self)
        openmultifiles.triggered.connect(self.get_multiple_filenames)
        openmultiidap = Widgets.QAction(Gui.QIcon(os.path.join(resourcedir,'open_multiple_idap.png')),'Open Multiple Idaps',self)
        openmultiidap.triggered.connect(self.open_multiple_idaps)
        standardquery = Widgets.QAction(Gui.QIcon(os.path.join(resourcedir,'standard_query.jpg')),'Standard Query',self)
        standardquery.triggered.connect(self.open_multiple_idaps)
        self.toolBar.addAction(opensinglefile)
        self.toolBar.addAction(openmultifiles)
        self.toolBar.addAction(openmultiidap)
        self.toolBar.addAction(standardquery)

    def setSearchWidget(self,text):
        self.searchBar.searchLine.setText('')
        if text == 'File':
            self.searchBar.widget = self.FileNameCombo
        elif text == 'Group':
            self.searchBar.widget = self.GroupNameCombo
        elif text == 'Dset':
            self.searchBar.widget = self.DatasetList
        elif text == 'Header':
            self.searchBar.widget = self.HeaderList

    def stopUpdater(self,tid):
        #This function stops the status indicator thread from updating.
        if not tid:
            print('No thread id was passed in stopUpdater.  Returning')
            return
        if tid not in self.threads:
            print('Thread id {} was not documented...  I dont know what to tell you'.format(tid))
            return
        self.threads[tid].stop()

    def killThread(self,tid):
        #self explanitory, however, it kills the thread based off a thread id
        #The thread id is used from pythons built in id() function call that
        #gives a unique id to each object created.
        if not tid:
            print('No thread id was passed in KillThread.  Returning')
            return
        if tid not in self.threads:
            print('Thread id {} was not documented...  I dont know what to tell you'.format(tid))
            return
        self.threads[tid].quit()
        self.threads.pop(tid)

    def closeEvent(self,event):
        #Do all the things when we close the GUI
        try:
            for thread in self.threads:
                self.threads[thread].quit()
        except:
            print('Some of the threads failed to quit... Maybe look into this')
        event.accept()

    def busy(self):
        #For when I want to disable the GUI
        self.setDisabled(True)
        Widgets.QApplication.processEvents()

    def ready(self):
        #For when I want to re-enable the GUI
        self.setEnabled(True)
        Widgets.QApplication.processEvents()

    def statusIndicatorStart(self):
        #Creates a thread to update a status indicator which is stored in
        #the layout self.StatusLayout
        thread = ProgressIndicatorUpdater(self.StatusLayout,self)
        threadkey = thread.getThreadId()
        self.threads[threadkey] = thread
        self.threads[threadkey].Stopped.connect(self.killThread)
        self.threads[threadkey].start()
        return threadkey

    def checkThrottle(self,lookahead):
        #This is a check for the number of cores vs the number of threads you
        #are trying to run.  Pops up a message box warning the user.
        if self.throttle:
            if len(self.threads)+int(lookahead) > self.numcores:
                Message =   'Number of available Threads is about to be exceeded.  Continue?'
                detailed =  'The process that you are attempting to start will'+\
                            ' use {} cores.  You are currently using '.format(lookahead)+\
                            '{} out of {} cores.  '.format(len(self.threads),self.numcores)+\
                            'This is not detrimental to your'.format(self.numcores)+\
                            ' system if the number of total cores used is not vastly greater'+\
                            ' than the number that is available.'
                title =     'Thread Warning'
                return QtUtils.MessageBox(Message,title=title,detail=detailed)
        return True

    def getExtension(self,fpath):
        return os.path.splitext(fpath)[1].strip().lower()

### DragNDrop

    def dropEvent(self,event):
        paths = QtUtils.dropFileDir(event)
        if paths:
            if len(paths) == 1:
                self.dragNdrop_filename(paths[0])
            else:
                self.dragNdrop_filenames(paths)
        else:
            self.Alert(self.statusbar,'No path information was found in the dropped file',error=True)

    def reset_file_widgets(self,rtype,**kwargs):
        self.FileNameCombo.blockSignals(True)
        self.GroupNameCombo.blockSignals(True)
        self.DatasetList.blockSignals(True)
        self.HeaderList.blockSignals(True)
        if rtype == 'File':
            self.FileNameCombo.clear()
            self.GroupNameCombo.clear()
            self.DatasetList.clear()
            self.HeaderList.clear()
        elif rtype == 'Group':
            self.GroupNameCombo.clear()
            self.DatasetList.clear()
            self.HeaderList.clear()
        elif rtype == 'Dset':
            self.DatasetList.clear()
            self.HeaderList.clear()
        elif rtype == 'Header':
            self.HeaderList.clear()
        self.FileNameCombo.blockSignals(False)
        self.GroupNameCombo.blockSignals(False)
        self.DatasetList.blockSignals(False)
        self.HeaderList.blockSignals(False)

### File Opening

    def check_file(self,fpath,**kwargs):
        extension = self.getExtension(fpath)
        for dfe in self.DataFileExtensions.itervalues():
            if extension.lower().endswith(dfe[0]):
                return True
        if extension.lower().endswith('.csv'):
            dialog = QtUtils.PandasCSVopener(fpath,self)
            dialog.complete.connect(lambda data,native:self.make_table_from_file(data,fpaths=[fpath],native=native))
            dialog.exec_()
            return False
        else:
            self.Alert(self.statusbar,'Extension {} is not supported.'.format(extension),error=True)
            return False

    def dragNdrop_filename(self,fpath,**kwargs):
        if self.check_file(fpath):
            self.reset_file_widgets('File')
            self.LastDirectory = os.path.dirname(fpath)
            self.FileNameCombo.addItem(os.path.basename(fpath))
            self.FileNameCombo.setCurrentIndex(0)

    def dragNdrop_filenames(self,paths,**kwargs):
        paths = [path for path in paths if self.check_file(path)]
        if paths:
            self.LastDirectory = os.path.dirname(paths[-1])
            self.reset_file_widgets('File')
            self.FileNameCombo.addItems(paths)
            self.FileNameCombo.setCurrentIndex(0)
        else:
            self.Alert(self.statusbar,'None of the dropped files were supported',error=True)

    def scan_directory(self,**kwargs):
        showstatus = kwargs.get('status',True)
        numthreads = 1
        if showstatus:
            numthreads = 2
        if not self.checkThrottle(numthreads):
            return
        if showstatus:
            tid = self.statusIndicatorStart()
        thread = RetrieveData(target=PhobosFunctions.gather_files,args=('/home/klinetry/Desktop/analytix-master/',),kwargs=dict(ext = ['*{}'.format(k[0]) for k in self.DataFileExtensions.itervalues()]))
        threadkey = thread.getThreadId()
        self.threads[threadkey] = thread
        self.threads[threadkey].statusTID = tid
        self.threads[threadkey].EmitRetrievedData.connect(self.populate_files)
        self.threads[threadkey].QueryFinished.connect(self.killThread)
        self.threads[threadkey].StatusPartner.connect(self.stopUpdater)
        self.threads[threadkey].start()

    def get_single_filename(self,**kwargs):
        fpath = QtUtils.openSingleFile(directory=self.LastDirectory,extensions=self.DataFileExtensions)
        if fpath:
            if self.check_file(fpath):
                self.reset_file_widgets('File')
                self.LastDirectory = os.path.dirname(fpath)
                self.FileNameCombo.addItem(os.path.basename(fpath))
                self.FileNameCombo.setCurrentIndex(0)
        else:
            self.Alert(self.statusbar,'No File Was Selected',wtime=1)

    def get_multiple_filenames(self,**kwargs):
        #TODO gotta be careful here, because all files may not come from same dir.. gotta keep track of that
        fpaths = QtUtils.openMultipleFiles(directory = self.LastDirectory,extensions=self.DataFileExtensions)
        fpaths = [path for path in fpaths if self.check_file(path)]
        if fpaths:
            self.LastDirectory = os.path.dirname(fpaths[-1])
            self.reset_file_widgets('File')
            self.FileNameCombo.addItems(os.path.basename(fpaths))
            self.FileNameCombo.setCurrentIndex(0)
        else:
            self.Alert(self.statusbar,'None of the selected files were supported',error=True)

    def open_multiple_idaps(self,**kwargs):
        runs = QtUtils.openRunListWidget(self.LastDirectory)


### File Group Dset and Header Population

    def populate_files(self,data,**kwargs):
        basedir = data[0]
        fnames = data[1]
        self.LastDirectory = basedir
        self.reset_file_widgets('File')
        self.FileNameCombo.addItems(fnames)
        self.FileNameCombo.setCurrentIndex(-1)

    def populate_groups(self,**kwargs):
        #TODO modify this to read from dsdicts
        if self.FileNameCombo.currentText():
            fpath = os.path.join(self.LastDirectory,self.FileNameCombo.currentText())
            grps = PhobosFunctions.get_groups(fpath)
            if grps:
                self.reset_file_widgets('Group')
                if len(grps) > 1:
                    index = -1
                else:
                    index = 0
                self.GroupNameCombo.addItems(sorted(grps))
                self.GroupNameCombo.setCurrentIndex(index)
            else:
                self.reset_file_widgets('File')
                self.Alert(self.statusbar,'There are no groups in {}.'.format(fpath),error=True)
        else:
            self.reset_file_widgets('Group')

    def populate_datasets(self,**kwargs):
        #TODO modify function to read from dsdict.. but Ill probably store it as a variable when i read groups
        if self.GroupNameCombo.currentText():
            fname = self.FileNameCombo.currentText()
            grp = self.GroupNameCombo.currentText()
            fpath = os.path.join(self.LastDirectory,fname)
            dsets = PhobosFunctions.get_dsets(fpath,grp,checkCommon=True)
            if dsets:
                self.reset_file_widgets('Dset')
                self.DatasetList.addItems(dsets)
                if not len(dsets) > 1:
                    #Select the dataset if there is only 1 there
                    self.DatasetList.setCurrentRow(0)
            else:
                self.reset_file_widgets('File')
                self.Alert(self.statusbar,'There are not datasets in {}/{}.'.format(fpath,grp),error=True)
        else:
            self.reset_file_widgets('Dset')

    def populate_headers(self,**kwargs):
        #TODO modify function to read from dsdict
        if self.DatasetList.count():
            fname = self.FileNameCombo.currentText()
            grp = self.GroupNameCombo.currentText()
            dset = QtUtils.returnListSelection(self.DatasetList,first=True)
            fpath = os.path.join(self.LastDirectory,fname)
            headers = PhobosFunctions.get_headers(fpath,grp,dset)
            if headers:
                self.reset_file_widgets('Header')
                self.HeaderList.addItems(headers)
            else:
                self.reset_file_widgets('File')
                self.Alert(self.statusbar,'There are no headers in {}/{}/{}.'.format(fpath,grp,dset),error=True)
        else:
            self.reset_file_widgets('Header')

### Data Getting

    def get_data_from_file(self,**kwargs):
        showstatus = kwargs.get('status',True)
        numthreads = 1
        if showstatus:
            numthreads = 2
        if not self.checkThrottle(numthreads):
            return
        if showstatus:
            tid = self.statusIndicatorStart()
        #TODO look at this
        fpath = os.path.join(self.LastDirectory,self.FileNameCombo.currentText())
        grp = self.GroupNameCombo.currentText()
        dset = QtUtils.returnListSelection(self.DatasetList,first=True)
        headers = QtUtils.returnListSelection(self.HeaderList)
        extension = self.getExtension(fpath)
        if extension in ['.h5','.hdf5']:
            func = PhobosFunctions.get_h5_data
            args = (fpath,grp,dset,)
            fpaths = [fpath]
            grps = [grp]
            dsets = [dset]
#        elif extension in ['.csv']:
#            func = PhobosFunctions.get_csv_data
        elif extension in ['.xlsx']:
            func = PhobosFunctions.get_xlsx_data
            args = (fpath,dset,)
            fpaths = [fpath]
            grps = []
            dsets = []
        elif extension in ['.pkl']:
            func = PhobosFunctions.get_pkl_data
            args = (fpath,)
            grps = []
            dsets = []
        else:
            self.Alert(self.statusbar,'The extension {} is not recognized in get_data_from_file.'.format(extension),error=True)
            return
        thread = RetrieveData(target=func,args=args,kwargs=dict(headers=headers,gatherpct=self.GatherPct.text()))
        threadkey = thread.getThreadId()
        self.threads[threadkey] = thread
        self.threads[threadkey].statusTID = tid
        self.threads[threadkey].EmitRetrievedData.connect(lambda data,native:self.make_table_from_file(data,fpaths=fpaths,native=native,grps=grps,dsets=dsets))
        self.threads[threadkey].QueryFinished.connect(self.killThread)
        self.threads[threadkey].StatusPartner.connect(self.stopUpdater)
        self.threads[threadkey].start()

    def get_native_header_data(self,headers,**kwargs):
        if not isinstance(headers,list):
            self.Alert('The headers to add to the table were not sent as a list',error=True)
            return pd.DataFrame()
        if self.TableTabWidget.count():
            twidget = self.TableTabWidget.currentWidget()

### Table Portion

    def make_table_from_file(self,data,**kwargs):
        #Assuming data is a dataframe
        if data.shape[0]:
            #Make fpaths a list, because in general we might have multiple files concated
            uniqueKey = uuid.uuid4()
            TableWidget = TabTableWidget(self,data,**kwargs)
            self.TableTabWidget.addTab(TableWidget,'Test')
            self.TableTabWidget.currentChanged.connect(self.AddNativeHeader.setList(self.TableTabWidget.currentWidget().addableHeaders))
        else:
            self.Alert(self.statusbar,'No Data was passed to make_table_from_file',error=True)

### Adding Data to Table

    def addNativeHeaders(self,data):
        #Need to search key of table
        #get table model and call addColumn
        if self.TableTabWidget.count() and data.shape[0]:
            twidget = self.TableTabWidget.currentWidget()
            twidget.model.addColumnData(data)
        print data

    def showdata(self,data):
        print data

    def done(self):
        print 'DONE'
        self.ready()

    def printSelected(self):
        if self.TableTabWidget.count():
            twidget = self.TableTabWidget.currentWidget()
            print 'IM HERE'
            print QtUtils.returnTableSelectedColumns(twidget.Table)
    def filterTable(self):
        if self.TableTabWidget.count():
            twidget = self.TableTabWidget.currentWidget()
            lent = twidget.model.rowCount()
            twidget.model.filterTable('')
#            twidget.model.addColumnData(pd.DataFrame({'This':['True']*lent}))


if __name__ == '__main__':
    import sys
    app = Widgets.QApplication(sys.argv)
    frame = Phobos()
    frame.show()
#    splash.finish(frame)
    retval = app.exec_()
    sys.exit(retval)
