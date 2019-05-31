# -*- coding: utf-8 -*-
"""
Created on Fri Dec 21 16:12:00 2018

@author: Jordan
"""

import matplotlib.font_manager as mplfm

import os
import sys
import numpy as np
import pandas as pd
import h5py
from glob import glob
import copy
import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui
import PyQt5.QtGui as QtWidgets
from PyQt5.Qt import *
from PyQt5 import QtSql
from PyQt5.QtCore import QVariant
from PyQt5 import QtSql, uic#, QtOpenGL
import operator
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.qt_compat import QtCore, QtWidgets, is_pyqt5
from matplotlib.backends.backend_qt5agg import (FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure
from matplotlib import colors as mcolors
import matplotlib.patches as mpatches
#import geopandas as gp
import cartopy
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.io.shapereader import Reader
import time
import Queue as queue
import LongFunc as lf
import h5_traj_generator as trajgen
import random

from mpl_toolkits.mplot3d import Axes3D
#sys.path.insert(0, 'C:\\Users\\Jordan\\Desktop\\Work Practice\\PyOpenGL_World_Py35_Qt5CarlVersion\\')
#import ota_world as otaw

RELATIVE_LIB_PATH = os.path.join(os.path.expanduser('~'),'PyModules')

COUNTRY_BOUNDS_SHP = os.path.join(RELATIVE_LIB_PATH,'Cartopy','ne_110m_admin_0_countries.shp')
COUNTRY_BOUNDS  = cfeature.ShapelyFeature(Reader(COUNTRY_BOUNDS_SHP).geometries(), ccrs.PlateCarree(), facecolor ='none', color='red',alpha=0.5)

import FilterClass
import InternationalDateline as ID

colors = dict(mcolors.BASE_COLORS, **mcolors.CSS4_COLORS)

# Sort colors by hue, saturation, value and name.
by_hsv = sorted((tuple(mcolors.rgb_to_hsv(mcolors.to_rgba(color)[:3])), name)
                for name, color in colors.items())
random.shuffle(by_hsv)
plotcolor = [name for hsv, name in by_hsv]
operators = ['Equal To','Less Than','Greater Than','Not Equal To','In Range','Not In Range','Starts With','Does Not Start With','Ends With','Does Not End With','Contains','Does Not Contain','Ascending Order','Descending Order']
plotsymb = ['.',',','o','v','^','<','>','8','s','P','p','*','h','H','D','d']
#plotcolor = ['blue','black','red','green']
maps = sorted(m for m in plt.cm.datad if not m.endswith("_r"))
orkeys = [str(i) for i in range(10)]
orkeys.insert(0,'')




import Plotterator as Plotterator
from collections import OrderedDict
plotcolor.append('COLORBAR')
TIMEFIELDS = ['ValidityTime_TALO','ScenarioTime_TALO','Time','time']
TRANSFORMS = ['Plate Carree','North Polar','EckertV','Rotated Pole']
cbartypes = ['Scatter','Timeline','Basemap','3D Plot']
linestyles = ['-','--']




#spath = 'C:\Users\Jordan\Desktop'
spath = os.getcwd()


def BMOACorrection(lat,lon,radius_km):
    arclength = radius_km
    re = 6371.
    angle = arclength*180/(np.pi*re)
    height = 2*angle
    width = 2*angle
    print height,width
    return height,width

class Plotter(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        uic.loadUi('Plotter.ui', self)
        self.thread = []
        self.tableList = {}
        self.tableIDList = []
#        self.HeaderCombo = []
#        self.HeaderOperator = []
#        self.UniqueValues = []
#        self.FilterOr = []
#        self.FilterAnd = []
        self.MasterData = {}
        self.plotList = [OrderedDict()]
#        self.plotColor = []
#        self.plotSymbol = []
        self.makeConnections()
        self.selectDirectory()
        self.popFileName()
        self.initPlot(False)
#        self.ColorBarNames.addItems(maps)
        self.colorbar = None
        self.NewPlot = False
        self.tableLayout = {}
        self.tableDimensions = {}
        self.tableWidget = {}
        self.showingGlobe = False
        
        self.plotlistSymbol = []
        self.plotlistColor = []
        self.Filter = FilterClass.FilterClass(self,self.FilterTree,connect=False)
        
    def Alert(self,msg,This=True,That=True):
        print msg
        
    def makeConnections(self):
        
        
        #The new ish
        self.FigureColorBtn.clicked.connect(lambda:self.colorPicker(self.FigureBackGroundColor))
        self.AxisColorBtn.clicked.connect(lambda:self.colorPicker(self.AxisBackGroundColor))
        self.PlotType.activated.connect(lambda:self.initPlot())
        self.PlotType.activated.connect(lambda:self.initPlotOptions())
        self.PlotType.currentIndexChanged.connect(self.StackedPlotOptions.setCurrentIndex)
        self.PlotColorSymbol.itemChanged.connect(lambda:self.updateCanvas())
        self.AddToPlotlist.clicked.connect(lambda:self.addToPlotList())
        self.PlotListPlot.clicked.connect(lambda:self.plotListPlot(Save=False))
        self.PlotListSave.clicked.connect(lambda:self.plotListPlot(Save=True))
        self.AdvancedOptions.clicked.connect(lambda:self.plotListAdvanced())
        self.setDynamicConnections()
        self.PlotListRemoveSelected.clicked.connect(lambda:self.clearPlotListSelection())
        self.PlotTree.itemSelectionChanged.connect(lambda:self.populatePlotListOptions())
        self.PlotOptionsTree.itemExpanded.connect(lambda:self.PlotOptionsTree.resizeColumnToContents(0))
        self.PlotOptionsTree.itemExpanded.connect(lambda:self.PlotOptionsTree.resizeColumnToContents(1))
        self.plotlistindex = 0
#        self.TableTab.currentChanged.connect(lambda:self.initPlot())
        
        
        
        self.TableTab.currentChanged.connect(lambda:self.PlotType.setCurrentIndex(0))
        self.FileName.activated.connect(self.popGroup)
        self.GroupName.activated.connect(self.popDset)
        self.DatasetList.currentItemChanged.connect(self.popHeaders)
        self.ClearHeaders.clicked.connect(self.HeaderList.clearSelection)
        self.ClearNative.clicked.connect(self.AddNativeHeaders.clearSelection)
        self.CreateTable.clicked.connect(self.addMasterData)
        self.TableTab.currentChanged.connect(self.addNativeHeaders)
        self.TableTab.currentChanged.connect(self.addFilterTree)
        self.AddFilter.clicked.connect(self.addFilters)
        self.FilterTree.itemChanged.connect(lambda:self.loadFilters())
        self.AddNative.clicked.connect(self.addNativeHeaderData)
        self.actionTimeline_Plotter.triggered.connect(lambda:self.stackedWidget.setCurrentIndex(1))
        self.actionGeneral_Plotter.triggered.connect(lambda:self.stackedWidget.setCurrentIndex(0))
        self.actionMerge_Table.triggered.connect(lambda:self.stackedWidget.setCurrentIndex(2))
        self.actionTestBed.triggered.connect(lambda:self.stackedWidget.setCurrentIndex(2))
        self.actionStat_Table.triggered.connect(lambda:self.addStatTable(True))
        
        self.TableTab.currentChanged.connect(self.setupMergeTablesCombo)
        self.TableNamesMergeCombo.activated.connect(self.populateMergeLists)
        self.MergeButton.clicked.connect(self.mergeTables)
        

#        self.TableTab.currentChanged.connect(lambda:self.initPlot(True))
#        self.PlotType.currentIndexChanged.connect(lambda:self.initPlot(True))
##        self.PlotType.currentIndexChanged.connect(self.initPlotOptions)
##        self.PlotType.currentIndexChanged.connect(self.setupPlotOptions)
##        self.UpdatePlot.clicked.connect(self.updateCanvas)
##        self.AddToPlotList.clicked.connect(self.addToPlotList)
#        self.PlotListRemoveSelected.clicked.connect(self.clearPlotListSelection)
#        self.ClearPlotList.clicked.connect(self.clearPlotList)
#        self.PlotListPlot.clicked.connect(self.plotFigures)
#        
##        self.SymbolCode.stateChanged.connect(lambda:self.initPlotOptions(False))
#        self.PlotTree.itemSelectionChanged.connect(self.initPlotListOptions)
#        self.UpdatePlotList.clicked.connect(self.updatePlotList)
#        self.SymbolCodeHeader.activated.connect(self.initPlotOptions)
        
        self.CalcPi.clicked.connect(self.Calc)
        return
    
    def selectDirectory(self):
#        self.indir = os.path.join(spath,'Project(Work)')
        self.indir = spath
        
    def popFileName(self):
        for file in os.listdir(self.indir):
            if file.endswith(".h5"):
                self.FileName.addItem(file)
        self.FileName.setCurrentIndex(-1)
        
    def popGroup(self):
        self.GroupName.clear()
        self.DatasetList.blockSignals(True)
        self.DatasetList.clear()
        self.DatasetList.blockSignals(False)
        self.HeaderList.clear()
        if self.FileName.currentText():
            fpath = os.path.join(self.indir,self.FileName.currentText())
            with h5py.File(fpath,'r') as hf:
                self.GroupName.addItems(hf.keys())
        self.GroupName.setCurrentIndex(-1)
                
    def popDset(self):
        self.DatasetList.blockSignals(True)
        self.DatasetList.clear()
        self.DatasetList.blockSignals(False)
        self.HeaderList.clear()
        fpath = os.path.join(self.indir,self.FileName.currentText())
        with h5py.File(fpath,'r') as hf:
            self.DatasetList.addItems(hf.keys())
            
    def popHeaders(self):
        self.HeaderList.clear()
        fpath = os.path.join(self.indir,self.FileName.currentText())
        dset = self.DatasetList.currentItem().text()
        with h5py.File(fpath,'r') as hf:
            self.HeaderList.addItems(hf[dset].dtype.fields.keys())
            
    def preTableData(self):
        return os.path.join(self.indir,self.FileName.currentText()),self.FileName.currentText(),self.GroupName.currentText(),self.DatasetList.currentItem().text()
            
    def addMasterData(self):
        if self.HeaderList.currentItem():
            path,filename,grp,dset = self.preTableData()
            key = path+filename+grp+dset
            self.MasterData[key] = {'SelH':[item.text() for item in self.HeaderList.selectedItems()],
                                   'AllH':[self.HeaderList.item(i).text() for i in range(self.HeaderList.count())],
                                   'AddH':[],
                                   'AddData':{},
                                   'Path':path,
                                   'Filename':filename,
                                   'Grp':grp,
                                   'Dset':dset,
                                   'Dsets':[item.text() for item in self.DatasetList.selectedItems()],
                                   'Filters':[],
                                   'PlotList':[]}
            self.createTable()
    
    def addNativeHeaders(self):
        if self.TableTab.count():
            self.AddNativeHeaders.clear()
            index = self.TableTab.currentIndex()
            keyID = self.tableIDList[index]
            md = self.MasterData[keyID]
            self.AddNativeHeaders.addItems(set(md['AllH'])-set(md['SelH']))
            self.initPlot()
            self.initPlotOptions()
    
    def addNativeHeaderData(self):
        if self.TableTab.count() and self.AddNativeHeaders.currentItem():
            index = self.TableTab.currentIndex()
            keyID = self.tableIDList[index]
            md = self.MasterData[keyID]
            addHeaders = [item.text() for item in self.AddNativeHeaders.selectedItems()]
            data = self.retrieveData(keyID,addHeaders)
            self.tableList[keyID].model().addColumnData(data,addHeaders)
            md['SelH'].extend(addHeaders)
            self.addNativeHeaders()
            self.addFilterTree()
    
    def removeHeaderData(self,header):
        if self.TableTab.count():
            index = self.TableTab.currentIndex()
            keyID = self.tableIDList[index]
            md = self.MasterData[keyID]
            if header in md['SelH']:
                self.tableList[keyID].model().removeColumnData([header])
                md['SelH'].pop(md['SelH'].index(header))
                self.addNativeHeaders()
                self.addFilterTree()
                
    def addNativeHeaderDatabyHeader(self,header):
        if self.TableTab.count():
            index = self.TableTab.currentIndex()
            keyID = self.tableIDList[index]
            md = self.MasterData[keyID]
            if header not in md['SelH']:
                data = self.retrieveData(keyID,addHeaders)
                self.tableList[keyID].model().addColumnData(data,header)
                md['SelH'].extend(addHeaders)
                self.addNativeHeaders()
                self.addFilterTree()
            
        
    def retrieveData(self,key,headers=None):
        md = self.MasterData[key]
        data = {}
        if not headers:
            headers = copy.copy(md['SelH'])
        with h5py.File(md['Path'], 'r') as hf:
            for header in headers:
                data[header] = hf[md['Dset']][header][0:200]
        return pd.DataFrame(data)
            
        
    def createTable(self):
        self.TableTab.blockSignals(True)
        path,filename,grp,dset = self.preTableData()
        key = path+filename+grp+dset
        md = self.MasterData[key]
        headers = copy.copy(md['SelH'])
        data = self.retrieveData(key)
        if key not in self.tableIDList:
            self.tableWidget[key] = QWidget()
            self.tableLayout[key] = QtWidgets.QVBoxLayout(self.tableWidget[key])
            self.tableLayout[key].addWidget(QLabel(os.path.join(path,grp,dset)))
            self.tableLayout[key].addWidget(QLabel('rows:'+str(data.shape[0])))
            self.tableList[key] = QTableView()
            self.tableLayout[key].addWidget(self.tableList[key])
            self.tableIDList.append(key)
            self.TableTab.addTab(self.tableWidget[key],md['Dset'])
        self.tableList[key].setModel(FieldTableModel(data,headers,self))
        self.tableList[key].selectionModel().selectionChanged.connect(self.initPlotOptions)
        self.addNativeHeaders()
        #new ish
        self.initPlotOptions()
        self.TableTab.blockSignals(False)
        self.headermenu = self.tableList[key].horizontalHeader()
        self.headermenu.setContextMenuPolicy(Qt.CustomContextMenu)
        self.headermenu.customContextMenuRequested.connect(self.headerPopup)
        self.TableTab.setCurrentIndex(self.TableTab.count()-1)
        
    def deleteTable(self,pos):
        tabbar = self.TableTab.tabBar()
        count = tabbar.count()
        for i in range(count):
            if tabbar.tabRect(i).contains(pos):
                index = i
                break
#        index = tabbar.logicalIndexAt(pos)
        keyID = self.tableIDList[index]
        menu = QMenu()
        DelAction = menu.addAction('Delete Table')
        action = menu.exec_(self.TableTab.mapToGlobal(pos))
        if action == DelAction:
            self.MasterData.pop(keyID,None)
            self.TableTab.removeTab(index)
            self.tableWidget.pop(keyID,None)
            self.tableLayout.pop(keyID,None)
            self.tableList.pop(keyID,None)
            self.tableIDList.pop(index)
        print self.MasterData
        
    def headerPopup(self,pos):
        index = self.TableTab.currentIndex()
        keyID = self.tableIDList[index]
        index = self.headermenu.logicalIndexAt(pos)
        md = self.MasterData[keyID]
        menu = QMenu()
        AOAction = menu.addAction('Ascending Order')
        DOAction = menu.addAction('Descending Order')
        DeleteAction = menu.addAction('Delete Header')
        action = menu.exec_(self.tableList[keyID].mapToGlobal(pos))
        if action == AOAction:
            md['Filters'].append([md['SelH'][index],'Ascending Order','',1,'',''])
            self.addFilterTree()
        if action == DOAction:
            md['Filters'].append([md['SelH'][index],'Descending Order','',1,'',''])
            self.addFilterTree()
        if action == DeleteAction:
            self.removeHeaderData(md['SelH'][index])
#        menu.destroy()
        
    def addFilters(self):
        if self.TableTab.count():
            index = self.TableTab.currentIndex()
            keyID = self.tableIDList[index]
            md = self.MasterData[keyID]
            self.Filter.addFilters(self.tableList[keyID],md['Filters'],md['SelH'])
#            headers = copy.copy(md['SelH'])
#            item = QTreeWidgetItem()
#            item.setFlags(item.flags() | Qt.ItemIsSelectable | Qt.ItemIsUserCheckable | Qt.ItemIsEditable)
#            self.HeaderCombo.append(QComboBox())
#            self.HeaderOperator.append(QComboBox())
#            self.FilterOr.append(QComboBox())
#            self.FilterAnd.append(QComboBox())
#            self.UniqueValues.append(QComboBox())
#            self.HeaderCombo[-1].addItems(headers)
#            self.HeaderOperator[-1].addItems(operators)
#            self.FilterOr[-1].addItems(orkeys)
#            self.FilterAnd[-1].addItems(orkeys)
#            item.setText(3,'')
#            item.setCheckState(0,Qt.Checked)
##            self.HeaderCombo[-1].activated.connect(self.loadFilters)
#            self.HeaderCombo[-1].activated.connect(self.uniqueValues)
#            self.HeaderOperator[-1].activated.connect(self.loadFilters)
#            self.FilterOr[-1].activated.connect(self.loadFilters)
#            self.FilterAnd[-1].activated.connect(self.loadFilters)
#            self.UniqueValues[-1].activated.connect(self.loadFilters)
#            self.HeaderCombo[-1].setCurrentIndex(0)
#            self.HeaderOperator[-1].setCurrentIndex(0)
#            self.FilterOr[-1].setCurrentIndex(-1)
#            self.FilterAnd[-1].setCurrentIndex(-1)
#            self.FilterTree.addTopLevelItem(item)
#            if self.tableList[keyID].model().getDtype(headers[0]) == 'O':
#                vals = self.tableList[keyID].model().getColumnData(headers[0])
#                self.UniqueValues[-1].addItems(pd.unique(vals))
#                self.FilterTree.setItemWidget(item,3,self.UniqueValues[-1])
#            self.FilterTree.setItemWidget(item,1,self.HeaderCombo[-1])
#            self.FilterTree.setItemWidget(item,2,self.HeaderOperator[-1])
#            self.FilterTree.setItemWidget(item,4,self.FilterOr[-1])
#            self.FilterTree.setItemWidget(item,5,self.FilterAnd[-1])
#            md['Filters'].append([self.HeaderCombo[-1].currentText(),self.HeaderOperator[-1].currentText(),item.text(3),0,self.FilterOr[-1].currentText(),self.FilterAnd[-1].currentText()])
            
    def loadFilters(self):
        if self.TableTab.count():
            index = self.TableTab.currentIndex()
            keyID = self.tableIDList[index]
            md = self.MasterData[keyID]
            self.Filter.loadFilters(self.tableList[keyID],md['Filters'],md['SelH'])
#            headers = copy.copy(md['SelH'])
#            
#            for i in range(self.FilterTree.topLevelItemCount()):
#                item = self.FilterTree.topLevelItem(i)
#                md['Filters'][i][0] = self.HeaderCombo[i].currentText()
#                md['Filters'][i][1] = self.HeaderOperator[i].currentText()
#                if self.tableList[keyID].model().getDtype(self.HeaderCombo[i].currentText()) == 'O':
#                    md['Filters'][i][2] = self.UniqueValues[-1].currentText()
#                else:
#                    md['Filters'][i][2] = item.text(3)
#                md['Filters'][i][4] = self.FilterOr[i].currentText()
#                md['Filters'][i][5] = self.FilterAnd[i].currentText()
#                if item.checkState(0) == Qt.Checked:
#                    md['Filters'][i][3] = 1
#                    procedures.append([md['Filters'][i][0],md['Filters'][i][1],md['Filters'][i][2],md['Filters'][i][4],md['Filters'][i][5]])
#                else:
#                    md['Filters'][i][3] = 0
#            self.tableList[keyID].model().filterTable(procedures)
            self.initPlotOptions()
            myWidget = self.tableLayout[keyID].itemAt(1).widget()
            myWidget.setText('rows:'+str(self.tableList[keyID].model().rowCount(0)))
            print 'did it'
#            self.addStatTable()
            
    def addFilterTree(self):
        if self.TableTab.count():
#            self.FilterTree.clear()
#            self.HeaderCombo = []
#            self.HeaderOperator = []
#            self.FilterOr = []
#            self.FilterAnd = []
            index = self.TableTab.currentIndex()
            keyID = self.tableIDList[index]
            md = self.MasterData[keyID]
            self.Filter.addFilterTree(self.tableList[keyID],md['Filters'],md['SelH'])
#            filts = md['Filters']
#            headers = copy.copy(md['SelH'])
#            for filt in filts:
#                if filt[0] not in headers:
#                    continue
#                item = QTreeWidgetItem()
#                item.setFlags(item.flags() | Qt.ItemIsSelectable | Qt.ItemIsUserCheckable | Qt.ItemIsEditable)
#                self.HeaderCombo.append(QComboBox())
#                self.HeaderOperator.append(QComboBox())
#                self.FilterOr.append(QComboBox())
#                self.FilterAnd.append(QComboBox())
#                self.UniqueValues.append(QComboBox())
#                self.HeaderCombo[-1].addItems(headers)
#                self.HeaderOperator[-1].addItems(operators)
#                self.FilterOr[-1].addItems(orkeys)         
#                self.FilterAnd[-1].addItems(orkeys)
#                item.setText(3,filt[2])
#                if filt[3] == 1:
#                    item.setCheckState(0,Qt.Checked)
#                else:
#                    item.setCheckState(0,Qt.Unchecked)
##                self.HeaderCombo[-1].activated.connect(self.loadFilters)
#                self.HeaderCombo[-1].activated.connect(self.uniqueValues)
#                self.HeaderOperator[-1].activated.connect(self.loadFilters)
#                self.FilterOr[-1].activated.connect(self.loadFilters)
#                self.FilterAnd[-1].activated.connect(self.loadFilters)
#                self.UniqueValues[-1].activated.connect(self.loadFilters)
#                index = self.HeaderCombo[-1].findText(filt[0])
#                self.HeaderCombo[-1].setCurrentIndex(index)
#                index = self.HeaderOperator[-1].findText(filt[1])
#                self.HeaderOperator[-1].setCurrentIndex(index)
#                index = self.FilterOr[-1].findText(filt[4])
#                self.FilterOr[-1].setCurrentIndex(index)
#                index = self.FilterAnd[-1].findText(filt[5])
#                self.FilterAnd[-1].setCurrentIndex(index)
#                if self.tableList[keyID].model().getDtype(headers[0]) == 'O':
#                    vals = self.tableList[keyID].model().getColumnData(headers[0])
#                    self.UniqueValues[-1].addItems(pd.unique(vals))
#                    index = self.UniqueValues[-1].findText(filt[4])
#                    self.UniqueValues[-1].setCurrentIndex(index)
#                    self.FilterTree.setItemWidget(item,3,self.UniqueValues[-1])
#                self.FilterTree.addTopLevelItem(item)
#                self.FilterTree.setItemWidget(item,1,self.HeaderCombo[-1])
#                self.FilterTree.setItemWidget(item,2,self.HeaderOperator[-1])
#                self.FilterTree.setItemWidget(item,4,self.FilterOr[-1])
#                self.FilterTree.setItemWidget(item,5,self.FilterAnd[-1])
#            self.loadFilters()
            
    def uniqueValues(self):
        if self.TableTab.count():
            index = self.TableTab.currentIndex()
            keyID = self.tableIDList[index]
            md = self.MasterData[keyID]
            self.Filter.uniqueValues(self.tableList[keyID],md['Filters'],md['SelH'])
#            for i in range(self.FilterTree.topLevelItemCount()):
#                item = self.FilterTree.topLevelItem(i)
#                if self.tableList[keyID].model().getDtype(self.HeaderCombo[i].currentText()) == 'O':
#                    vals = self.tableList[keyID].model().getColumnData(self.HeaderCombo[i].currentText())
#                    self.UniqueValues[i] = QComboBox()
#                    self.UniqueValues[i].addItems(pd.unique(vals))
#                    self.FilterTree.setItemWidget(item,3,self.UniqueValues[i])
#                    item.setText(3,'')
#                else:
#                    try:
#                        txt = item.text(3)
#                    except:
#                        txt = ''
#                    self.UniqueValues[i].clear()
#                    self.FilterTree.removeItemWidget(item,3)
#                    item.setText(3,txt)
#            self.loadFilters()
    def addNativeHeadersbyHeader(self,headers):
        index = self.TableTab.currentIndex()
        keyID = self.tableIDList[index]
        md = self.MasterData[keyID]
        model = self.tableList[keyID].model()
        for header in headers:
            if header in md['AllH']:
                data = self.retrieveData(keyID,[header])
                model.addColumnData(data,[header])
    
    def BaseMapLatLons(self):
        if self.TableTab.count():
            types = []
            self.GetTypeLatLon.clear()
            index = self.TableTab.currentIndex()
            keyID = self.tableIDList[index]
            md = self.MasterData[keyID]
            hdrchk = set(md['AllH']+md['SelH'])
            if set(['Lat','Lon']).issubset(hdrchk) or set(['lat','lon']).issubset(hdrchk):
                self.addNativeHeadersbyHeader(['Lat','Lon'])
                types.append('Lat/Lon')
            if set(['ImpactLat','ImpactLon']).issubset(hdrchk) or set(['impactLat','impactLon']).issubset(hdrchk):
                self.addNativeHeadersbyHeader(['ImpactLat','ImpactLon'])
                types.append('Impact Lat/Lon')
            if set(['LaunchLat','LaunchLon']).issubset(hdrchk) or set(['launchLat','launchLon']).issubset(hdrchk):
                self.addNativeHeadersbyHeader(['LaunchLat','LaunchLon'])
                types.append('Launch Lat/Lon')
            if set(['Lat','Lon','Circle_Radius']).issubset(hdrchk):
                self.addNativeHeadersbyHeader(['Lat','Lon','Circle_Radius'])
                types.append('Bmoas CR')
            if set(['Lat','Lon','Radius']).issubset(hdrchk):
                self.addNativeHeadersbyHeader(['Lat','Lon','Radius'])
                types.append('Bmoas R')
            if types == []:
                self.Alert("No Lat Lon Data found in dataset",True)
            self.GetTypeLatLon.clear()
            self.GetTypeLatLon.addItems(types)
            self.GetTypeLatLon.setCurrentIndex(-1)
    
    def tformMapper(self):
        if isinstance(self.Transform,QComboBox):
            text = self.Transform.currentText()
            if text == 'Plate Carree':
                return ccrs.PlateCarree()
            if text == 'North Polar':
                return ccrs.NorthPolarStereo()
            if text == 'EckertV':
                return ccrs.EckertV()
            if text == 'Rotated Pole':
                return ccrs.RotatedPole()
            
    def setDynamicConnections(self):
        for i in range(self.StackedPlotOptions.count()):
            self.StackedPlotOptions.setCurrentIndex(i)
            parent = self.StackedPlotOptions.currentWidget()
            qcombos = parent.findChildren(QComboBox)
            qlines = parent.findChildren(QLineEdit)
            qcheck = parent.findChildren(QCheckBox)
            qlabel = parent.findChildren(QLabel)
            qslider = parent.findChildren(QSlider)
            for widget in qcombos:
                if 'Transform' in widget.objectName():
                    widget.setCurrentIndex(-1)
                    widget.activated.connect(lambda:self.initPlotOptions())
                    widget.activated.connect(lambda:self.Alert('Transform'))
                if 'ColorbarName' in widget.objectName():
                    colorbarname = widget
                    widget.setCurrentIndex(-1)
                    widget.activated.connect(lambda:self.initPlotOptions())
                    widget.activated.connect(lambda:self.Alert('Colorbarname'))
                if 'TypeLatLon' in widget.objectName():
                    widget.setCurrentIndex(-1)
                    widget.activated.connect(lambda:self.initPlotOptions())
                    widget.activated.connect(lambda:self.Alert('latlon'))
                if 'ColorbarHeader' in widget.objectName():
                    colorbarheader = widget
                    widget.setCurrentIndex(-1)
                    widget.activated.connect(lambda:self.initPlotOptions())
                    widget.activated.connect(lambda:self.Alert('Colorbarheader'))
                if 'XAxis' in widget.objectName():
                    widget.activated.connect(lambda:self.updateCanvas())
                    widget.activated.connect(lambda:self.Alert('xcombo'))
                    widget.setCurrentIndex(-1)
                if 'SymbolCode' in widget.objectName():
                    symbolcodecombo = widget
                    widget.setCurrentIndex(-1)
                    widget.activated.connect(lambda:self.initPlotOptions())
                    widget.activated.connect(lambda:self.Alert('symbolcodecombo'))
            for widget in qlines:
                if 'ColorbarLabel' in widget.objectName():
                    colorbarlabel = widget
                    widget.setText('')
                    widget.editingFinished.connect(lambda:self.updateCanvas())
                    widget.editingFinished.connect(lambda:self.Alert('colorbarlabel'))
                if 'BackGroundColor' in widget.objectName():
                    widget.setText('#FFFFFF')
                    palette.setColor(widget.backgroundRole(),QtGui.QColor(255,255,255))
            for widget in qlabel:
                widget.blockSignals(True)
                if 'MarkerSize' in widget.objectName():
                    markersize = widget
                if 'LineWidth' in widget.objectName():
                    linewidth = widget
                if 'BarWidth' in widget.objectName():
                    barwidth = widget
                if 'BinNum' in widget.objectName():
                    binnum = widget
                if 'AlphaSize' in widget.objectName():
                    alpha = widget
                widget.blockSignals(False)
            for widget in qslider:
                if 'BarWidthSlider' in widget.objectName():
                    widget.sliderMoved.connect(barwidth.setNum)
                    widget.sliderMoved.connect(lambda:self.updateCanvas())
                    widget.sliderMoved.connect(lambda:self.Alert('barwidth'))
                if 'MarkerSlider' in widget.objectName():
                    widget.sliderMoved.connect(markersize.setNum)
                    widget.sliderMoved.connect(lambda:self.updateCanvas())
                    widget.sliderMoved.connect(lambda:self.Alert('markerslider'))
                if 'LineSlider' in widget.objectName():
                    widget.sliderMoved.connect(linewidth.setNum)
                    widget.sliderMoved.connect(lambda:self.updateCanvas())
                    widget.sliderMoved.connect(lambda:self.Alert('lineslider'))
                if 'BinNumSlider' in widget.objectName():
                    widget.sliderMoved.connect(binnum.setNum)
                    widget.sliderMoved.connect(lambda:self.updateCanvas())
                    widget.sliderMoved.connect(lambda:self.Alert('binnum'))
                if 'AlphaSlider' in widget.objectName():
                    widget.sliderMoved.connect(alpha.setNum)
                    widget.sliderMoved.connect(lambda:self.updateCanvas())
                    widget.sliderMoved.connect(lambda:self.Alert('alphaslider'))
            for widget in qcheck:
                widget.setChecked(False)
                if 'SymbolCodeCheckBox' in widget.objectName():
                    widget.toggled.connect(colorbarlabel.setDisabled)
                    widget.toggled.connect(colorbarheader.setDisabled)
                    widget.toggled.connect(colorbarname.setDisabled)
                    widget.toggled.connect(symbolcodecombo.setEnabled)
                    widget.toggled.connect(lambda:self.initPlotOptions())
                    widget.toggled.connect(lambda:self.Alert('symbolcodecheck'))
                if 'FillDA' in widget.objectName():
                    widget.toggled.connect(lambda:self.updateCanvas())
                    widget.toggled.connect(lambda:self.Alert('fill da'))
        self.StackedPlotOptions.setCurrentIndex(0)
        
    def initPlot(self, doOption=True):
        if self.TableTab.count():
            index = self.TableTab.currentIndex()
            keyID = self.tableIDList[index]
        self.Transform = QComboBox()
        self.ColorbarNameCombo = QComboBox()
        self.ColorbarHeaderCombo = QComboBox()
        self.XAxisCombo = QComboBox()
        self.SymbolCodeCombo = QComboBox()
        self.MarkerSize = QLabel()
        self.LineWidth = QLabel()
        self.ColorbarLabel = QLineEdit()
        self.BinNum = QLabel()
        self.BarWidth = QLineEdit()
        self.SymbolCodeChk = QCheckBox()
        self.GetTypeLatLon = QComboBox()
        parent = self.StackedPlotOptions.currentWidget()
        qcombos = parent.findChildren(QComboBox)
        qlines = parent.findChildren(QLineEdit)
        qcheck = parent.findChildren(QCheckBox)
        qlabel = parent.findChildren(QLabel)
        qslider = parent.findChildren(QSlider)
        for widget in qcombos:
            if 'Transform' in widget.objectName():
                self.Transform = widget
                self.Transform.clear()
                self.Transform.addItems(TRANSFORMS)
                widget.setCurrentIndex(0)
            if 'ColorbarName' in widget.objectName():
                self.ColorbarNameCombo = widget
                widget.setCurrentIndex(-1)
            if 'TypeLatLon' in widget.objectName():
                self.GetTypeLatLon = widget
                widget.setCurrentIndex(-1)
            if 'ColorbarHeader' in widget.objectName():
                self.ColorbarHeaderCombo = widget
                widget.setCurrentIndex(-1)
            if 'XAxis' in widget.objectName():
                self.XAxisCombo = widget
                widget.setCurrentIndex(-1)
            if 'SymbolCode' in widget.objectName():
                self.SymbolCodeCombo = widget
                widget.setCurrentIndex(-1)
        for widget in qlabel:
            widget.blockSignals(True)
            if 'MarkerSize' in widget.objectName():
                self.MarkerSize = widget
            if 'LineWidth' in widget.objectName():
                self.LineWidth = widget
            if 'BarWidth' in widget.objectName():
                self.BarWidth = widget
            if 'BinNum' in widget.objectName():
                self.BinNum = widget
            if 'AlphaSize' in widget.objectName():
                self.alpha = widget
            widget.blockSignals(False)
        for widget in qlines:
            if 'ColorbarLabel' in widget.objectName():
                self.ColorbarLabel = widget
                widget.setText('')
            if 'BackGroundColor' in widget.objectName():
                widget.setText('#FFFFFF')
                palette.setColor(widget.backgroundRole(),QtGui.QColor(255,255,255))
#        for widget in qslider:
#            if 'BarWidthSlider' in widget.objectName():
#                widget.sliderMoved.connect(self.BarWidth.setNum)
#            if 'MarkerSlider' in widget.objectName():
#                widget.sliderMoved.connect(self.MarkerSize.setNum)
#            if 'LineSlider' in widget.objectName():
#                widget.sliderMoved.connect(self.LineWidth.setNum)
#            if 'BinNumSlider' in widget.objectName():
#                widget.sliderMoved.connect(self.BinNum.setNum)
        for widget in qcheck:
            widget.setChecked(False)
            if 'SymbolCodeCheckBox' in widget.objectName():
                self.SymbolCodeChk = widget
#                widget.toggled.connect(self.ColorbarLabel.setDisabled)
#                widget.toggled.connect(self.ColorbarHeaderCombo.setDisabled)
#                widget.toggled.connect(self.ColorbarNameCombo.setDisabled)
#                widget.toggled.connect(self.SymbolCodeCombo.setEnabled)
#                widget.toggled.connect(lambda:self.initPlotOptions())
        self.BaseMapLatLons()
        self.makeAxis()
    def makeAxis(self):
        if self.TableTab.count():
            index = self.TableTab.currentIndex()
            keyID = self.tableIDList[index]
            md = self.MasterData[keyID]
        types = self.PlotType.currentText()
        for i in reversed(range(self.PlotLayout.count())):
            widgetToRemove = self.PlotLayout.itemAt(i).widget()
            self.PlotLayout.removeWidget(widgetToRemove)
            widgetToRemove.deleteLater()
        self.dynamic_canvas = FigureCanvas(Figure())
        plotCanvasLabel = QLabel()
        plotCanvasLabel.setText('Preview of Plot.  Figure can be saved using toolbar.')
        plotCanvasLabel.setAlignment(Qt.AlignCenter)
        self.PlotLayout.addWidget(NavigationToolbar(self.dynamic_canvas,self))
        self.PlotLayout.addWidget(plotCanvasLabel)
        self.PlotLayout.addWidget(self.dynamic_canvas)
        
        if types not in ['Basemap','3D Plot']:
            self.ZAxisLabel.setEnabled(False)
            self._dynamic_ax = self.dynamic_canvas.figure.subplots() 
            self._dynamic_ax.figure.tight_layout()
            self._dynamic_ax.set_aspect('auto')
        elif types == 'Basemap':
            self.ZAxisLabel.setEnabled(False)
            self._dynamic_ax = self.dynamic_canvas.figure.subplots(subplot_kw={'projection':ccrs.PlateCarree()})
            self._dynamic_ax.figure.tight_layout()
            self._dynamic_ax.set_aspect('auto')
        elif types == '3D Plot':
            self.ZAxisLabel.setEnabled(True)
            self._dynamic_ax = Axes3D(self.dynamic_canvas.figure)
            self._dynamic_ax.figure.tight_layout()
            self._dynamic_ax.set_aspect('auto')
            if self.TableTab.count():
                if set(['PosX','PosY','PosZ']).issubset(set(md['AllH']+md['AddH'])):
                    self.addNativeHeadersbyHeader(['PosX','PosY','PosZ'])
                elif set(['X','Y','Z']).issubset(set(md['AllH']+md['AddH'])):
                    self.addNativeHeadersbyHeader(['X','Y','Z'])
                else:
                    self.Alert("No x,y,z data found in dataset",True)
                
    def initPlotOptions(self, TypeChange=True):
        if self.TableTab.count():
            self.makeAxis()
            self.plotColor = []
            self.plotSymbol = []
            self.plotLine = []
            self.PlotColorSymbol.clear()
            index = self.TableTab.currentIndex()
            keyID = self.tableIDList[index]
            md = self.MasterData[keyID]
            model = self.tableList[keyID].model()
            table = self.tableList[keyID]
            headers = model.getHeaderNames()
            nsheaders = []
            uniqueheaders = []
            for header in headers:
                if model.getDtype(header) != 'O':
                    nsheaders.append(header)
                if len(pd.unique(model.getColumnData(header))) < 50:
                    uniqueheaders.append(header)
            
            self.PlotColorSymbol.blockSignals(True)
#            self.Transform.clear()
#            self.Transform.addItems(TRANSFORMS)
            ColorbarNameCombo = self.ColorbarNameCombo.currentText()
            self.ColorbarNameCombo.clear()
            self.ColorbarNameCombo.addItems(maps)
            index = self.ColorbarNameCombo.findText(ColorbarNameCombo)
            self.ColorbarNameCombo.setCurrentIndex(index)
            ColorbarHeaderCombo = self.ColorbarHeaderCombo.currentText()
            self.ColorbarHeaderCombo.clear()
            self.ColorbarHeaderCombo.addItem('')
            self.ColorbarHeaderCombo.addItems(nsheaders)
            index = self.ColorbarHeaderCombo.findText(ColorbarHeaderCombo)
            self.ColorbarHeaderCombo.setCurrentIndex(index)
            XAxisName = self.XAxisCombo.currentText()
            self.XAxisCombo.clear()
            self.XAxisCombo.addItems(headers)
            index = self.XAxisCombo.findText(XAxisName)
            if index < 0:
                for header in headers:
                    if header in TIMEFIELDS:
                        index = self.XAxisCombo.findText(header)
                        break
                
            self.XAxisCombo.setCurrentIndex(index)
            codeName = self.SymbolCodeCombo.currentText()
            self.SymbolCodeCombo.clear()
            self.SymbolCodeCombo.addItems(uniqueheaders)
            index = self.SymbolCodeCombo.findText(codeName)
            self.SymbolCodeCombo.setCurrentIndex(index)
            
            if self.PlotType.currentText() in cbartypes:
                if self.ColorbarHeaderCombo.currentText() and not self.ColorbarNameCombo.currentText() and not self.SymbolCodeChk.isChecked():
                    self.ColorbarNameCombo.setCurrentIndex(0)
                    self.SymbolCodeCombo.setCurrentIndex(-1)
                elif self.ColorbarNameCombo.currentText() and not self.ColorbarHeaderCombo.currentText() and not self.SymbolCodeChk.isChecked():
                    if self.ColorbarHeaderCombo.currentIndex() == 0:
                        self.ColorbarNameCombo.setCurrentIndex(-1)
                    else:
                        self.ColorbarHeaderCombo.setCurrentIndex(0)
                        self.SymbolCodeCombo.setCurrentIndex(-1)
                elif self.ColorbarNameCombo.currentText() and self.ColorbarHeaderCombo.currentText() and not self.SymbolCodeChk.isChecked():
                    ColorbarNameCombo = self.ColorbarNameCombo.currentText()
                    self.ColorbarNameCombo.clear()
                    self.ColorbarNameCombo.addItems(maps)
                    index = self.ColorbarNameCombo.findText(ColorbarNameCombo)
                    self.ColorbarNameCombo.setCurrentIndex(index)
                    ColorbarHeaderCombo = self.ColorbarHeaderCombo.currentText()
                    self.ColorbarHeaderCombo.clear()
                    self.ColorbarHeaderCombo.addItem('')
                    self.ColorbarHeaderCombo.addItems(nsheaders)
                    index = self.ColorbarHeaderCombo.findText(ColorbarHeaderCombo)
                    self.ColorbarHeaderCombo.setCurrentIndex(index)
                    self.SymbolCodeCombo.setCurrentIndex(-1)
                elif self.SymbolCodeChk.isChecked() and not self.SymbolCodeCombo.currentText():
                    self.SymbolCodeCombo.setCurrentIndex(0)
                    self.ColorbarHeaderCombo.setCurrentIndex(-1)
                    self.ColorbarNameCombo.setCurrentIndex(-1)
                    self.ColorbarLabel.setText('')
                elif self.SymbolCodeChk.isChecked() and self.SymbolCodeCombo.currentText():
                    self.ColorbarHeaderCombo.setCurrentIndex(-1)
                    self.ColorbarNameCombo.setCurrentIndex(-1)
                    self.ColorbarLabel.setText('')
                else:
                    self.SymbolCodeCombo.setCurrentIndex(-1)
                    self.ColorbarHeaderCombo.setCurrentIndex(-1)
                    self.ColorbarNameCombo.setCurrentIndex(-1)
                    self.ColorbarLabel.setText('')
            else:
                self.SymbolCodeCombo.setCurrentIndex(-1)
                self.ColorbarHeaderCombo.setCurrentIndex(-1)
                self.ColorbarNameCombo.setCurrentIndex(-1)
                self.ColorbarLabel.setText('')
            if self.PlotType.currentText() == '3D Plot':
                self.ZAxisLabel.setEnabled(True)
            else:
                self.ZAxisLabel.setEnabled(False)
            if self.PlotType.currentText() == 'Pie':
                self.YAxisLabel.setEnabled(False)
            else:
                self.YAxisLabel.setEnabled(True)
            if self.PlotType.currentText() == 'Basemap':
                for i in reversed(range(self.PlotLayout.count())):
                    widgetToRemove = self.PlotLayout.itemAt(i).widget()
                    self.PlotLayout.removeWidget(widgetToRemove)
                    widgetToRemove.deleteLater()
                
                self.dynamic_canvas = FigureCanvas(Figure())
                plotCanvasLabel = QLabel()
                plotCanvasLabel.setText('Preview of Plot.  Figure can be saved using toolbar.')
                plotCanvasLabel.setAlignment(Qt.AlignCenter)
                self.PlotLayout.addWidget(NavigationToolbar(self.dynamic_canvas,self))
                self.PlotLayout.addWidget(plotCanvasLabel)
                self.PlotLayout.addWidget(self.dynamic_canvas)
                self.ZAxisLabel.setEnabled(False)
                self._dynamic_ax = self.dynamic_canvas.figure.subplots(subplot_kw={'projection':self.tformMapper()})
                self._dynamic_ax.figure.tight_layout()
                self._dynamic_ax.set_aspect('auto')
            if self.PlotType.currentText() == 'Bar':
                self.XAxisCombo.setCurrentIndex(0)
                self.XAxisCombo.setEnabled(False)
            else:
                self.XAxisCombo.setEnabled(True)
            if self.PlotType.currentText() not in ['Basemap','3D Plot','Pie']:
                if table.selectionModel().selectedColumns():
                    for i,index in enumerate(table.selectionModel().selectedColumns()):
                        if not self.SymbolCodeChk.isChecked():
                            self.addToPlotSymbolColor(headers[index.column()],'All',headers[index.column()],i)
                        else:
                            if self.SymbolCodeCombo.currentText():
                                uniquequants = pd.unique(model.getColumnData(self.SymbolCodeCombo.currentText()))
                                for j,val in enumerate(uniquequants):
                                    self.addToPlotSymbolColor(self.SymbolCodeCombo.currentText(),str(val),self.SymbolCodeCombo.currentText()+':'+str(val),j)
            elif self.PlotType.currentText() in ['Basemap','3D Plot']:
                if not self.SymbolCodeChk.isChecked():
                    self.addToPlotSymbolColor('Coordinates','All','N/A for this type',0)
                else:
                    if self.SymbolCodeCombo.currentText():
                        uniquequants = pd.unique(model.getColumnData(self.SymbolCodeCombo.currentText()))
                        for j,val in enumerate(uniquequants):
                            self.addToPlotSymbolColor(self.SymbolCodeCombo.currentText(),str(val),self.SymbolCodeCombo.currentText()+':'+str(val),0)
            self.updateCanvas()
            self.PlotColorSymbol.blockSignals(False)
    
    def addToPlotSymbolColor(self,HEADER,VALUE,LEGENDNAME,Index):
        item = QTreeWidgetItem()
        self.plotSymbol.append(QComboBox())
        self.plotColor.append(QComboBox())
        self.plotLine.append(QComboBox())
        self.plotSymbol[-1].addItems(plotsymb)
        self.plotColor[-1].addItems(plotcolor)
        item.setText(0,HEADER)
        item.setText(1,VALUE)
        item.setText(4,LEGENDNAME)
        item.setFlags(item.flags()|Qt.ItemIsEditable)
        self.plotColor[-1].activated.connect(self.updateCanvas)
        self.plotSymbol[-1].activated.connect(self.updateCanvas)
        self.PlotColorSymbol.addTopLevelItem(item)
        if self.PlotType.currentText() in ['Line']:
            self.plotLine[-1].addItems(linestyles)
            self.plotLine[-1].activated.connect(self.updateCanvas)
            self.PlotColorSymbol.setItemWidget(item,1,self.plotLine[-1])
        if self.PlotType.currentText() in ['Bar','Stacked']:
            item.setText(3,'N/A')
        else:
            self.PlotColorSymbol.setItemWidget(item,3,self.plotSymbol[-1])
        self.PlotColorSymbol.setItemWidget(item,2,self.plotColor[-1])
        self.plotColor[-1].setCurrentIndex(Index%len(plotcolor))
        self.plotSymbol[-1].setCurrentIndex(Index%len(plotsymb))
        
    
    def updateSymbolCodes(self):
        if self.SymbolCodeChk.isChecked():
            self.SymbolCodeChk.setChecked(False)
    
    def colorPicker(self,widget):
        if isinstance(widget,QLineEdit):
            color = QColorDialog.getColor()
            widget.setText(color.name())
            palette = QPalette()
            palette.setColor(widget.backgroundRole(),color)
            widget.setAutoFillBackground(True)
            widget.setPalette(palette)
            widget.setText(color.name())
        else:
            print('The color widget is not a QLineEdit')
            
    def closeAllPlots(self):
        plt.close('all')
        
    def updateCanvas(self):
        if self.TableTab.count():
            dax = self._dynamic_ax
            dax.clear()
            dax.figure.legends=[]
            dax.set_aspect('auto')
            plotBmoa = False
            plxlabel = ''
            plylabel = ''
            plzlabel = ''
            pltitle = ''
            plx,ply,plz = [],[],[]
            pllinestyle = []
            pllinewidth = 0
            plspacing = []
            plbarwidth = 0
            plbinnum = 0
            plalpha = 0
            plradii = []
            plxAxisDataHeader = ''
            plplottedheaders = []
            plcolor = []
            plcm = None
            pluniquevals = []
            plmarker = []
            plmarkersize = 0
            pllegends = []
            plcolorbarlabel = ''
            plprojection = ''
            addedcolorbar = False
            plnsheaders = []
            pluniqueheaders = []
            plfillDA = False

            ptype = self.PlotType.currentText()
            if self.XAxisCombo.currentText():
                index = self.TableTab.currentIndex()
                keyID = self.tableIDList[index]
                table = self.tableList[keyID]
                model = table.model()
                headers = model.getHeaderNames()
                md = self.MasterData[keyID]
                if self.colorbar:
                    try:
                        self.colorbar.remove()
                    except:
                        pass
                pltitle = self.PlotTitle.text()
                if self.XAxisLabel.text():
                    plxlabel = self.XAxisLabel.text()
                else:
                    plxlabel = self.XAxisCombo.currentText()
                
                if ptype in ['Scatter','Timeline','Stacked','Line'] and table.selectionModel().selectedColumns():
                    for index in table.selectionModel().selectedColumns():
                        if self.SymbolCodeChk.isChecked() and self.PlotColorSymbol.topLevelItemCount():
                            pluniquevals = pd.unique(model.getColumnData(self.SymbolCodeCombo.currentText()))
                            uniquedata = model.getColumnData(self.SymbolCodeCombo.currentText())
                            xdata = model.getColumnData(self.XAxisCombo.currentText())
                            if ptype in ['Scatter']:
                                ydata = model.getColumnData(headers[index.column()])
                            elif ptype == 'Timeline':
                                ydata = np.array([md['Dset']+headers[index.column()]]*xdata.size)
                            for i,val in enumerate(pluniquevals):
                                idx = uniquedata == val
                                if True in idx:
                                    ply.append(ydata[idx])
                                    plx.append(xdata[idx])
                        else:
                            
                            if ptype in ['Scatter','Stacked','Line']:
                                if ptype == 'Stacked':
                                    if ply:
                                        if ply[0].dtype.kind != model.getDtype(headers[index.column()]): 
                                            continue
                                sorteddata = pd.DataFrame({'x':model.getColumnData(self.XAxisCombo.currentText()),'y':model.getColumnData(headers[index.column()])})
                                sorteddata.sort_values('x',inplace=True)
                                ply.append(sorteddata['y'])
                                plx.append(sorteddata['x'])
                            elif ptype in ['Timeline']:
                                ply.append(np.array([md['Dset']+headers[index.column()]]*model.getColumnData(self.XAxisCombo.currentText()).size))
                                plx.append(model.getColumnData(self.XAxisCombo.currentText()))
                            pluniquevals = [0]
                        plplottedheaders.append(headers[index.column()])
                        if self.YAxisLabel.text():
                            plylabel = self.YAxisLabel.text()
                        else:
                            if plylabel == '':
                                plylabel = headers[index.column()]
                            else:
                                plylabel = plylabel + ' / ' + headers[index.column()]
                    if ptype not in ['Stacked']:
                        plmarkersize = int(str(self.MarkerSize.text()))
                    else:
                        plmarkersize = None
                    for i,ydat in enumerate(ply):
                        item = self.PlotColorSymbol.topLevelItem(i)
                        plmarker.append(self.plotSymbol[i].currentText())
                        pllegends.append(item.text(4))
                        if ptype in cbartypes:
                            if self.ColorbarHeaderCombo.currentText() and not self.SymbolCodeChk.isChecked():
                                addedcolorbar = True
                                self.plotColor[i].setCurrentIndex(len(plotcolor)-1)
                                plcolor.append(model.getColumnData(self.ColorbarHeaderCombo.currentText()))
                                plcm = plt.cm.get_cmap(self.ColorbarNameCombo.currentText())
                            else:
                                plcolor.append(self.plotColor[i].currentText())
                                plcm = None
                        else:
                            plcolor.append(self.plotColor[i].currentText())
                            plcm = None
                        if ptype in ['Scatter','Timeline']:
                            sc = dax.scatter(plx[i],ydat,s = plmarkersize, c = plcolor[i], cmap = plcm, marker = plmarker[i], label = pllegends[i])
                        if ptype in ['Line']:
                            pllinewidth = int(self.LineWidth.text())
                            pllinestyle.append(self.plotLine[i].currentText())
                            sorteddata = pd.DataFrame({'x':plx[i],'y':ydat})
                            sorteddata.sort_values('x',inplace=True)
                            sc = dax.plot(sorteddata['x'],sorteddata['y'],ms = plmarkersize, color = plcolor[i], marker = plmarker[i],label = pllegends[i],linestyle = pllinestyle[i], linewidth = pllinewidth)
                    if ptype in ['Stacked']:
                        ply = [np.row_stack(ply)]
                        sc = dax.stackplot(plx[0],ply[0],colors=[colorss for colorss in plcolor],labels=[labelss for labelss in pllegends])
                    if ptype in cbartypes:
                        if self.ColorbarHeaderCombo.currentText() and not self.SymbolCodeChk.isChecked():
                            addedcolorbar = True
                            self.colorbar = dax.figure.colorbar(sc)
                            if self.ColorbarLabel.text():
                                plcolorbarlabel = self.ColorbarLabel.text()
                            else:
                                plcolorbarlabel = self.ColorbarHeaderCombo.currentText()
                            self.colorbar.set_label(plcolorbarlabel)
                    plxAxisDataHeader = self.XAxisCombo.currentText()
                if ptype == 'Pie':
                    dax.set_aspect(1)
                    plbinnum = int(self.BinNum.text())
                    x = model.getColumnData(self.XAxisCombo.currentText())
                    cmap = plt.cm.jet
                    if len(pd.unique(x)) > 20 and x.dtype.kind != 'O':
                        bins = np.linspace(x.min(),x.max(),plbinnum+1)
                        y = pd.cut(x,bins)
                        plx = y.value_counts().sort_index()
                        plcolor = cmap(np.linspace(0.,1.,plbinnum))
                    else:
                        u = len(pd.unique(x))
                        plcolor = cmap(np.linspace(0.,1.,u))
                        plx = x.value_counts().sort_index()
                    pllegends = map(str,plx.index.tolist())
                    plxAxisDataHeader = self.XAxisCombo.currentText()
                    sc = dax.pie(plx,autopct = '%.2f%%',colors=plcolor)
                    if not self.HideLegend.isChecked():
                        dax.figure.legend(pllegends,prop=mplfm.FontProperties(size=6),loc='best',ncol=4).draggable()

                if ptype =='Bar':
                    if self.YAxisLabel.text():
                        plylabel = self.YAxisLabel.text()
                    else:
                        plylabel = 'Number Of Occurences'
                    for i,index in enumerate(table.selectionModel().selectedColumns()):
                        x = model.getColumnData(headers[index.column()])
                        plplottedheaders.append(headers[index.column()])
#                        if len(pd.unique(x)) < 50:
                        plx.append(x)
                        plspacing.append(np.arange(len(pd.unique(x))))
#                        else:
#                            self.Alert("Too many unique values in "+str(headers[index.column()]),True)
#                            pass
                    plxAxisDataHeader = plplottedheaders
                    if plx:
                        plbarwidth = float(self.BarWidth.text())/len(plx)
                    else:
                        plbarwidth = 0
                    
                    for i,ydat in enumerate(plx):
                        
                        item = self.PlotColorSymbol.topLevelItem(i)
                        pllegends.append(item.text(4))
                        plcolor.append(self.plotColor[i].currentText())
                        if ydat.dtype.kind =='f':
                            ticklabels = [str(round(float(val),2)) for val in ydat.value_counts().index]
                        else:
                            ticklabels = ydat.value_counts().index
                        sc = dax.bar(plspacing[i] + i*plbarwidth, ydat.value_counts(),plbarwidth*.8,color = plcolor[i],tick_label=ticklabels,label=pllegends[i])                
                    dax.set_aspect('auto')
                    
                if ptype in ['Basemap']:
                    lltext = self.GetTypeLatLon.currentText()
                    if lltext:
                        if lltext == 'Lat/Lon':
                            Lat = 'Lat'
                            Lon = 'Lon'
                        elif lltext == 'Impact Lat/Lon':
                            Lat = 'ImpactLat'
                            Lon = 'ImpactLon'
                        elif lltext == 'impact Lat/Lon':
                            Lat = 'impactLat'
                            Lon = 'impactLon'
                        elif lltext == 'Launch Lat/Lon':
                            Lat = 'LaunchLat'
                            Lon = 'LaunchLon'
                        elif lltext == 'launch Lat/Lon':
                            Lat = 'launchLat'
                            Lon = 'launchLon'
                        elif lltext == 'Bmoas CR':
                            Lat = 'Lat'
                            Lon = 'Lon'
                            Radius = 'Circle_Radius'
                            plotBmoa = True
                        elif lltext == 'Bmoas R':
                            Lat = 'Lat'
                            Lon = 'Lon'
                            Radius = 'Radius'
                            plotBmoa = True
                    else:
                        return
                    if plotBmoa:
                        bmoaradii = model.getColumnData(Radius)
                        plradii.append(bmoaradii)
                        plalpha = float(self.alpha.text())/100.0
                        plfillDA = self.BasemapFillDAChk.isChecked()
                    else:
                        plradii = None
#                        pass
                    if self.SymbolCodeChk.isChecked() and not plotBmoa:
                        ydata = model.getColumnData(Lat)
                        pluniquevals = pd.unique(model.getColumnData(self.SymbolCodeCombo.currentText()))
                        uniquedata = model.getColumnData(self.SymbolCodeCombo.currentText())
                        xdata = model.getColumnData(Lon)
                        for i,val in enumerate(pluniquevals):
                            idx = uniquedata == val
                            if True in idx:
                                ply.append(ydata[idx])
                                plx.append(xdata[idx])
                    elif self.SymbolCodeChk.isChecked() and plotBmoa:
                        plradii = []
                        ydata = model.getColumnData(Lat)
                        pluniquevals = pd.unique(model.getColumnData(self.SymbolCodeCombo.currentText()))
                        uniquedata = model.getColumnData(self.SymbolCodeCombo.currentText())
                        xdata = model.getColumnData(Lon)
                        for i,val in enumerate(pluniquevals):
                            idx = uniquedata == val
                            if True in idx:
                                ply.append(ydata[idx].reset_index(drop=True))
                                plx.append(xdata[idx].reset_index(drop=True))
                                plradii.append(bmoaradii[idx].reset_index(drop=True))
                    else:
                        ply.append(model.getColumnData(Lat))
                        plx.append(model.getColumnData(Lon))
                        pluniquevals = [0]
                    plmarkersize = int(self.MarkerSize.text())
                    #CHECK
                    plprojection = self.tformMapper()
                    dax.add_feature(COUNTRY_BOUNDS)                    
                    for i,ydat in enumerate(ply):
                        item = self.PlotColorSymbol.topLevelItem(i)
                        plmarker.append(self.plotSymbol[i].currentText())
                        pllegends.append(item.text(4))
                        if self.ColorbarHeaderCombo.currentText() and not self.SymbolCodeChk.isChecked() and not plotBmoa:
                            addedcolorbar = True
                            self.plotColor[i].setCurrentIndex(len(plotcolor)-1)
                            plcolor.append(model.getColumnData(self.ColorbarHeaderCombo.currentText()))
                            plcm = plt.cm.get_cmap(self.ColorbarNameCombo.currentText())
                        else:
                            plcolor.append(self.plotColor[i].currentText())
                            plcm = None
                        if not plotBmoa:
                            sc = dax.scatter(plx[i],ydat,s = plmarkersize, c = plcolor[i], cmap = plcm, marker = plmarker[i], label = pllegends[i], transform = ccrs.PlateCarree())
                            plxAxisDataHeader = 'Lon'
                        elif plotBmoa:
                            for j,r in enumerate(plradii[i]):
#                                BMOACorrection()
                                if r > 0:
                                    lats,lons = ID.circleLatLons(ply[i][j],plx[i][j],r)
                                    lats,lons = ID.handle_InternationalDateline(lats,lons)
                                else:
                                    lats,lons = ID.handle_InternationalDateline(ply[i][j],plx[i][j])
                                for ii in range(len(lats)):
                                    dax.add_patch(mpatches.Polygon(xy=np.array([lons[ii],lats[ii]]).T,closed = True,fill = plfillDA,color=plcolor[i],alpha=plalpha,transform=ccrs.PlateCarree(),zorder=30))
                                plxAxisDataHeader = 'Lon'
                    if self.ColorbarHeaderCombo.currentText() and not self.SymbolCodeChk.isChecked() and not plotBmoa:
                        self.colorbar = dax.figure.colorbar(sc)
                        if self.ColorbarLabel.text():
                            plcolorbarlabel = self.ColorbarLabel.text()
                        else:
                            plcolorbarlabel = self.ColorbarHeaderCombo.currentText()
                        self.colorbar.set_label(plcolorbarlabel)
                    dax.set_adjustable('datalim')
                    dax.set_aspect('equal')
                    dax.set_extent([-180,180,-90,90],crs=ccrs.PlateCarree())
                    dax.outline_patch.set_linewidth(0)
            
                if ptype == '3D Plot':
                    if 'PosX' in md['SelH']:
                        posy = 'PosY'
                        posx = 'PosX'
                        posz = 'PosZ'
                    elif 'X' in md['SelH']:
                        posy = 'Y'
                        posx = 'X'
                        posz = 'Z'
                    if self.SymbolCodeChk.isChecked():
                        ydata = model.getColumnData(posy)
                        xdata = model.getColumnData(posx)
                        zdata = model.getColumnData(posz)
                        pluniquevals = pd.unique(model.getColumnData(self.SymbolCodeCombo.currentText()))
                        uniquedata = model.getColumnData(self.SymbolCodeCombo.currentText())
                        for i,val in enumerate(pluniquevals):
                            idx = uniquedata == val
                            if True in idx:
                                ply.append(ydata[idx])
                                plx.append(xdata[idx])
                                plz.append(zdata[idx])
                    else:
                        ply.append(model.getColumnData(posy))
                        plx.append(model.getColumnData(posx))
                        plz.append(model.getColumnData(posz))
                        pluniquevals = [0]
                    if self.XAxisLabel.text():
                        plxlabel = self.XAxisLabel.text()
                    else:
                        plxlabel = 'X'
                    if self.YAxisLabel.text():
                        plylabel = self.YAxisLabel.text()
                    else:
                        plylabel = 'Y'
                    if self.ZAxisLabel.text():
                        plzlabel = self.ZAxisLabel.text()
                    else:
                        plzlabel = 'Z'
                    plmarkersize = int(self.MarkerSize.text())
                    for i in range(len(ply)):
                        item = self.PlotColorSymbol.topLevelItem(i)
                        plmarker.append(self.plotSymbol[i].currentText())
                        pllegends.append(item.text(4))
                        if self.ColorbarHeaderCombo.currentText() and not self.SymbolCodeChk.isChecked():
                            addedcolorbar = True
                            self.plotColor[i].setCurrentIndex(len(plotcolor)-1)
                            plcolor.append(model.getColumnData(self.ColorbarHeaderCombo.currentText()))
                            plcm = plt.cm.get_cmap(self.ColorbarNameCombo.currentText())
                        else:
                            plcolor.append(self.plotColor[i].currentText())
                            plcm = None
                        sc = dax.scatter(plx[i],ply[i],plz[i],zdir='z',s=plmarkersize,c=plcolor[i],cmap=plcm,marker=plmarker[i],label=pllegends[i])
                    if self.ColorbarHeaderCombo.currentText() and not self.SymbolCodeChk.isChecked():
                        self.colorbar = dax.figure.colorbar(sc)
                        if self.ColorbarLabel.text():
                            plcolorbarlabel = self.ColorbarLabel.text()
                        else:
                            plcolorbarlabel = self.ColorbarHeaderCombo.currentText()
                        self.colorbar.set_label(plcolorbarlabel)
                    dax.set_zlabel(plzlabel)
                    plxAxisDataHeader = 'x'

                if not self.HideLegend.isChecked():
                    dax.figure.legend(prop=mplfm.FontProperties(size=6),loc='best',ncol=4).draggable()
                if self.FigureBackGroundColor.text():
                    dax.figure.set_facecolor(self.FigureBackGroundColor.text())
                if self.AxisBackGroundColor.text():
                    dax.set_facecolor(self.AxisBackGroundColor.text())
                dax.set_title(pltitle)
                dax.set_xlabel(plxlabel)
                if len(plylabel) > 10:
                    dax.set_ylabel('default')
                else:
                    dax.set_ylabel(plylabel)
                dax.figure.tight_layout()
                dax.figure.canvas.draw()
                self.NewPlot = True
                self.Alert("why",False,True)
                if plcolor != []:
#                    if not isinstance(plxAxisDataHeader,list) and'time' in plxAxisDataHeader.lower():
#                        plxAxisDataHeader = 'Time'
#                    self.plotList[-1] = {'fig':pltr.fig,
#                                         'sub':pltr.sub,
#                                         'xaxis':plxAxisDataHeader,
#                                         'yaxis':plplottedheaders,
#                                         'colorbar':addedcolorbar,
#                                         'index':len(self.plotList),
#                                         'native':True,
#                                         'keyID':keyID,
#                                         'path':md['Path'],
#                                         'filename':md['Filename'],
#                                         'group':md['Grp'],
#                                         'dset':md['Dset'],
#                                         'plotType':ptype,
#                                         }
                    for header in headers:
                        if model.getDtype(header) != 'O':
                            plnsheaders.append(header)
                        if len(pd.unique(model.getColumnData(header))) < 50:
                            pluniqueheaders.append(header)
                    self.plotList[-1]['x label']=plxlabel
                    self.plotList[-1]['y label']=plylabel
                    self.plotList[-1]['z label']=plzlabel
                    self.plotList[-1]['plot title']=pltitle
                    self.plotList[-1]['x data']=plx
                    self.plotList[-1]['y data']=ply
                    self.plotList[-1]['z data']=plz
                    self.plotList[-1]['line style']=pllinestyle
                    self.plotList[-1]['line width']=pllinewidth
                    self.plotList[-1]['spacing']=plspacing
                    self.plotList[-1]['bar width']=plbarwidth
                    self.plotList[-1]['bin num']=plbinnum
                    self.plotList[-1]['bmoa']=plotBmoa
                    self.plotList[-1]['radii']=plradii
                    self.plotList[-1]['x axis data header']=plxAxisDataHeader
                    self.plotList[-1]['y axis data header']=plplottedheaders
                    self.plotList[-1]['symbol code']=self.SymbolCodeChk.isChecked()
                    self.plotList[-1]['symbol code header']=self.SymbolCodeCombo.currentText()
                    self.plotList[-1]['color']=plcolor
                    self.plotList[-1]['color map']=plcm
                    self.plotList[-1]['colorbar']=addedcolorbar
                    self.plotList[-1]['color map header']=self.ColorbarHeaderCombo.currentText()
                    self.plotList[-1]['color map name']=self.ColorbarNameCombo.currentText()
                    self.plotList[-1]['alpha']=plalpha
                    self.plotList[-1]['fill DA']=plfillDA
                    self.plotList[-1]['unique values']=pluniquevals
                    self.plotList[-1]['marker']=plmarker
                    self.plotList[-1]['marker size']=plmarkersize
                    self.plotList[-1]['legend']=pllegends
                    self.plotList[-1]['colorbar Label']=plcolorbarlabel
                    self.plotList[-1]['keyID']=keyID
                    self.plotList[-1]['path']=md['Path']
                    self.plotList[-1]['filename']=md['Filename']
                    self.plotList[-1]['group']=md['Grp']
                    self.plotList[-1]['dset']=md['Dset']
                    self.plotList[-1]['plot type']=ptype
                    self.plotList[-1]['index']=self.plotlistindex
                    self.plotList[-1]['projection']=plprojection
                    self.plotList[-1]['filters']=self.MasterData[keyID]['Filters']
                    self.plotList[-1]['non string headers']=plnsheaders
                    self.plotList[-1]['unique headers']=pluniqueheaders

    
    def addToPlotList(self,addtomaster=True):
        if self.TableTab.count():
            index = self.TableTab.currentIndex()
            keyID = self.tableIDList[index]
            md = self.MasterData[keyID]
            pl = self.plotList[-1]
            if pl:
                if addtomaster:
                    md['PlotList'].append(pl)
                item = QTreeWidgetItem()
                item.setText(0,pl['filename'])
                item.setText(1,pl['plot type'])
                item.setText(2,'filler')
                item.setText(3,str(pl['x axis data header']))
                item.setText(4,str(pl['y axis data header']))
                item.setText(5,str(pl['index']))
                item.setText(6,'filler')
                self.PlotTree.addTopLevelItem(item)
                self.plotList.append(OrderedDict())
                self.tableList[keyID].clearSelection()
                self.initPlot()
                self.initPlotOptions()
                self.plotlistindex += 1
                return
            
    def clearPlotListSelection(self):
        indecies = []
        for i in range(self.PlotTree.topLevelItemCount()-1,-1,-1):
            if self.PlotTree.topLevelItem(i).isSelected():
                indecies.append(i)
                item = self.PlotTree.topLevelItem(i)
                index = int(item.text(5))
                for key in self.MasterData:
                    for j,pl in enumerate(self.MasterData[key]['PlotList']):
                        if pl != {}:
                            if index == pl['index']:
                                self.MasterData[key]['PlotList'].pop(j)
                self.plotList.pop(index)
                self.PlotTree.takeTopLevelItem(i)
        return
    
    def clearPlotList(self):
        self.PlotTree.clear()
        self.plotList = [OrderedDict()]
        for key in self.MasterData:
            self.MasterData[key]['PlotList'] = []
            
    def getUniqueXAxis(self,keys):
        xaxis = {}
        for i in range(self.PlotTree.topLevelItemCount()):
            for key in keys:
                if self.PlotTree.topLevelItem(i).isSelected():
                    ptype = self.PlotTree.topLevelItem(i).text(1)
                    index = int(self.PlotTree.topLevelItem(i).text(5))
                    itemtext = self.PlotTree.topLevelItem(i).text(3)
                    if ptype in key:
                        if key not in xaxis:
                            xaxis[key] = []
                        xaxis[key].append(itemtext)
        for key in xaxis:
            xaxis[key] = pd.unique(xaxis[key])
        return xaxis
    
    def populatePlotListOptions(self):
        self.includelists = []
        self.dictionary = OrderedDict()
        for i in range(self.PlotTree.topLevelItemCount()):
            if self.PlotTree.topLevelItem(i).isSelected():
                includelist = []
                self.dictionary['Plot List Index:'+str(self.plotList[i]['index'])] = OrderedDict(self.plotList[i].items())
                if self.plotList[i]['plot type'] == 'Scatter':
                    includelist.extend(['plot title','x label','y label','marker size','marker','symbol code','color','colorbar','marker',\
                                        'legend'])
                if self.plotList[i]['plot type'] == 'Line':
                    includelist.extend(['plot title','x label','y label','marker size','marker','color','marker',\
                                        'legend','line style','line width'])
                if self.plotList[i]['plot type'] == 'Timeline':
                    includelist.extend(['plot title','x label','y label','marker size','marker','symbol code','color','colorbar','marker',\
                                        'legend'])
                if self.plotList[i]['plot type'] == 'Stacked':
                    includelist.extend(['plot title','x label','y label','marker size','marker','color','marker',\
                                        'legend'])
                if self.plotList[i]['plot type'] == 'Bar':
                    includelist.extend(['plot title','x label','y label','color','bar width',\
                                        'legend'])
                if self.plotList[i]['plot type'] == 'Pie':
                    includelist.extend(['plot title','x label',\
                                        'legend'])
                if self.plotList[i]['plot type'] == 'Basemap':
                    includelist.extend(['plot title','x label','y label','marker size','marker','symbol code','color','colorbar','marker',\
                                        'legend','projection','alpha','fill da']) 
                if self.plotList[i]['plot type'] == '3D Plot':
                    includelist.extend(['plot title','x label','y label','z label','marker size','marker','symbol code','color','colorbar','marker',\
                                        'legend'])
                    
                self.includelists.append(includelist)
        self.setupTreeWidget(self.PlotOptionsTree,self.dictionary,self.includelists)
        pass
                
    def plotListAdvanced(self):
        self.plotListPlot(Advanced=True)
    ### TREE WIDGET STUFF
    def setupTreeWidget(self,widget,treedata,includelists):
        treedata = OrderedDict(treedata.items())
        self.PlotOptionsTree.clear()
        widget.blockSignals(True)
        self.nestedwidgets = {k:{} for k in treedata.keys()}
        for k in treedata.keys():
            self.nestedwidgets[k]['colorcontainer'] = QWidget()
            self.nestedwidgets[k]['legendcontainer'] = QWidget()
            self.nestedwidgets[k]['markercontainer'] = QWidget()
        def walkDict(d,parent,key):
            d = OrderedDict(d)
            index = int(key.split(':')[-1])
            for k, v in d.iteritems():
                if k not in includelist:
                    continue
                child = QTreeWidgetItem(parent)
                if not isinstance(k,str):
                    k = str(k)
                child.setText(0,k)
                child.setCheckState(0, Qt.Unchecked)
                if isinstance(v, dict):
                    child.setFlags(child.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)
                    v = walkDict(v,child,key)
                #Line edit for single values
                if k in ['x label','y label','z label','plot title']:
                    self.nestedwidgets[key][k] = QLineEdit(v)
                    grandchild = QTreeWidgetItem(child)
                    widget.setItemWidget(grandchild,0,self.nestedwidgets[key][k])
                    self.nestedwidgets[key][k].textChanged.connect(lambda trash, plwidget=self.nestedwidgets[key][k],plindex=index,plkey=k:self.EditPlotOptions(plwidget,plindex,plkey,None))
                #Sliders for single values
                if k in ['line width','bar width','bin num','alpha','markersize']:
                    self.nestedwidgets[key][k] = QSlider(Qt.Horizontal)
                    self.nestedwidgets[key][k].setMinimum(1)
                    self.nestedwidgets[key][k].setMaximum(99)
                    self.nestedwidgets[key][k].setValue(v)
                    grandchild = QTreeWidgetItem(child)
                    widget.setItemWidget(grandchild,0,self.nestedwidgets[key][k])
                    self.nestedwidgets[key][k].valueChanged.connect(lambda plwidget=self.nestedwidgets[key][k],plindex=index,plkey=k:self.EditPlotOptions(plwidget,plindex,plkey,None))
                #Combo Box for list values
                if k in ['fill DA']:
                    self.nestedwidgets[key][k]=[]                    
                    self.nestedwidgets[key][k].append(QComboBox())
                    self.nestedwidgets[key][k][-1].addItems(['True','False'])
                    lsindex = self.nestedwidgets[key][k][-1].findText(str(d[k]))
                    self.nestedwidgets[key][k][-1].setCurrentIndex(lsindex)
                    grandchild = QTreeWidgetItem(child)
                    widget.setItemWidget(grandchild,0,self.nestedwidgets[key][k][-1])
                    activate = self.nestedwidgets[key][k][-1].currentText()
                    self.nestedwidgets[key][k][-1].currentIndexChanged.connect(lambda trash, plwidget=self.nestedwidgets[key][k][-1],plindex=index,plkey=k:self.EditPlotOptions(plwidget,plindex,plkey,None))
                if k in ['line style']:
                    self.nestedwidgets[key][k] = []
                    for i,item in enumerate(v):
                        self.nestedwidgets[key][k].append(QComboBox())
                        self.nestedwidgets[key][k][-1].clear()
                        self.nestedwidgets[key][k][-1].addItems(linestyles)
                        grandchild = QTreeWidgetItem(child)
                        widget.setItemWidget(grandchild,0,self.nestedwidgets[key][k][-1])
                        self.nestedwidgets[key][k][-1].currentIndexChanged.connect(lambda trash, plwidget=self.nestedwidgets[key][k][-1],plindex=index,plkey=k,pllistindex=i:self.EditPlotOptions(plwidget,plindex,plkey,pllistindex))
                if k in ['marker','color']:
                    self.nestedwidgets[key][k] = []
                    mylayout = QVBoxLayout()
                    for i,item in enumerate(v):
                        self.nestedwidgets[key][k].append(QComboBox())
                        self.nestedwidgets[key][k][-1].clear()
                        if k == 'marker':
                            container = 'markercontainer'
                            self.nestedwidgets[key][k][-1].addItems(plotsymb)
                        if k == 'color':
                            container = 'colorcontainer'
                            self.nestedwidgets[key][k][-1].addItems(plotcolor)
                            if isinstance(item,str) or isinstance(item,unicode):
                                lsindex = self.nestedwidgets[key][k][-1].findText(item)
                                self.nestedwidgets[key][k][-1].setCurrentIndex(lsindex)
                                self.nestedwidgets[key][k][-1].setEnabled(True)
                            else:
                                lsindex = self.nestedwidgets[key][k][-1].findText('COLORBAR')
                                self.nestedwidgets[key][k][-1].setCurrentIndex(lsindex)
                                self.nestedwidgets[key][k][-1].setEnabled(False)
                        else: 
                            lsindex = self.nestedwidgets[key][k][-1].findText(item)
                            self.nestedwidgets[key][k][-1].setCurrentIndex(lsindex)
                        mylayout.addWidget(self.nestedwidgets[key][k][-1])
                        self.nestedwidgets[key][k][-1].currentIndexChanged.connect(lambda trash, plwidget=self.nestedwidgets[key][k][-1],plindex=index,plkey=k,pllistindex=i:self.EditPlotOptions(plwidget,plindex,plkey,pllistindex))
                    self.nestedwidgets[key][container].setLayout(mylayout)
                    grandchild = QTreeWidgetItem(child)
                    widget.setItemWidget(grandchild,0,self.nestedwidgets[key][container])
                #Line edit for list values
                if k in ['legend']:
                    container = 'legendcontainer'
                    self.nestedwidgets[key][k] = []
                    mylayout = QVBoxLayout()
                    for i,item in enumerate(v):
                        self.nestedwidgets[key][k].append(QLineEdit(item))
#                        grandchild = QTreeWidgetItem(child)
#                        widget.setItemWidget(grandchild,0,self.nestedwidgets[key][k][-1])
                        self.nestedwidgets[key][k][-1].textChanged.connect(lambda trash, plwidget=self.nestedwidgets[key][k][-1],plindex=index,plkey=k,pllistindex=i:self.EditPlotOptions(plwidget,plindex,plkey,pllistindex))
                        mylayout.addWidget(self.nestedwidgets[key][k][-1])
                    self.nestedwidgets[key][container].setLayout(mylayout)
                    grandchild = QTreeWidgetItem(child)
                    widget.setItemWidget(grandchild,0,self.nestedwidgets[key][container])
                
                #Colorbar stuff
                if k in ['colorbar']:
                    intable = d['keyID'] in self.MasterData
                    self.nestedwidgets[key][k]=[]
                    #0 label
                    self.nestedwidgets[key][k].append(QLabel('has colorbar:'))
                    grandchild = QTreeWidgetItem(child)
                    widget.setItemWidget(grandchild,0,self.nestedwidgets[key][k][-1])
                    
                    #1 has colorbar combo
                    self.nestedwidgets[key][k].append(QComboBox())
                    self.nestedwidgets[key][k][-1].addItems(['True','False'])
                    lsindex = self.nestedwidgets[key][k][-1].findText(str(d['colorbar']))
                    self.nestedwidgets[key][k][-1].setCurrentIndex(lsindex)
                    grandchild = QTreeWidgetItem(child)
                    widget.setItemWidget(grandchild,0,self.nestedwidgets[key][k][-1])
                    activate = self.nestedwidgets[key][k][-1].currentText()
                    self.nestedwidgets[key][k][-1].currentIndexChanged.connect(lambda trash, plwidget=self.nestedwidgets[key][k][-1],plindex=index,plkey=k,dictkey=key:self.handleColorbar(plwidget,plindex,plkey,dictkey))
                    self.nestedwidgets[key][k][-1].currentIndexChanged.connect(lambda trash, plwidget=self.nestedwidgets[key][k][-1],plindex=index,plkey='colorbar':self.EditPlotOptions(plwidget,plindex,plkey,None))
                    if not intable:
                        self.nestedwidgets[key][k][-1].setEnabled(False)
                    
                    #2 label
                    self.nestedwidgets[key][k].append(QLabel('color map header:'))
                    grandchild = QTreeWidgetItem(child)
                    widget.setItemWidget(grandchild,0,self.nestedwidgets[key][k][-1])
                    
                    #3 colorbar headers
                    self.nestedwidgets[key][k].append(QComboBox())
                    if intable:
                        self.nestedwidgets[key][k][-1].addItems(d['non string headers'])
                    else:
                        self.nestedwidgets[key][k][-1].addItems([d['color map header']])
                    lsindex = self.nestedwidgets[key][k][-1].findText(str(d['color map header']))
                    self.nestedwidgets[key][k][-1].setCurrentIndex(lsindex)
                    grandchild = QTreeWidgetItem(child)
                    widget.setItemWidget(grandchild,0,self.nestedwidgets[key][k][-1])
                    if activate == 'False':
                        self.nestedwidgets[key][k][-1].setEnabled(False)
                    if not intable:
                        self.nestedwidgets[key][k][-1].setEnabled(False)
                    self.nestedwidgets[key][k][-1].currentIndexChanged.connect(lambda trash, plwidget=self.nestedwidgets[key][k][1],plindex=index,plkey=k,dictkey=key:self.handleColorbar(plwidget,plindex,plkey,dictkey))
                    self.nestedwidgets[key][k][-1].currentIndexChanged.connect(lambda trash,plwidget=self.nestedwidgets[key][k][-1],plindex=index,plkey='color map header':self.EditPlotOptions(plwidget,plindex,plkey,None))
                    
                    #4 label
                    self.nestedwidgets[key][k].append(QLabel('color map name:'))
                    grandchild = QTreeWidgetItem(child)
                    widget.setItemWidget(grandchild,0,self.nestedwidgets[key][k][-1])
                    
                    #5 colorbar map
                    self.nestedwidgets[key][k].append(QComboBox())
                    self.nestedwidgets[key][k][-1].addItems(maps)
                    lsindex = self.nestedwidgets[key][k][-1].findText(str(d['color map name']))
                    self.nestedwidgets[key][k][-1].setCurrentIndex(lsindex)
                    grandchild = QTreeWidgetItem(child)
                    widget.setItemWidget(grandchild,0,self.nestedwidgets[key][k][-1])
                    if activate == 'False':
                        self.nestedwidgets[key][k][-1].setEnabled(False)
#                    if not intable:
#                        self.nestedwidgets[key][k][-1].setEnabled(False)
                    self.nestedwidgets[key][k][-1].currentIndexChanged.connect(lambda trash, plwidget=self.nestedwidgets[key][k][1],plindex=index,plkey=k,dictkey=key:self.handleColorbar(plwidget,plindex,plkey,dictkey))
                    self.nestedwidgets[key][k][-1].currentIndexChanged.connect(lambda trash,plwidget=self.nestedwidgets[key][k][-1],plindex=index,plkey='color map name':self.EditPlotOptions(plwidget,plindex,plkey,None))
                    
                    #6 label
                    self.nestedwidgets[key][k].append(QLabel('colorbar label:'))
                    grandchild = QTreeWidgetItem(child)
                    widget.setItemWidget(grandchild,0,self.nestedwidgets[key][k][-1])
                    
                    #7 colorbar laabel
                    self.nestedwidgets[key][k].append(QLineEdit(str(d['colorbar Label'])))
                    grandchild = QTreeWidgetItem(child)
                    widget.setItemWidget(grandchild,0,self.nestedwidgets[key][k][-1])
                    if activate == 'False':
                        self.nestedwidgets[key][k][-1].setEnabled(False)
                    if not intable:
                        self.nestedwidgets[key][k][-1].setEnabled(False)
#                    self.nestedwidgets[key][k][-1].editingFinished.connect(lambda trash, plwidget=self.nestedwidgets[key][k][1],plindex=index,plkey=k,dictkey=key:self.handleColorbar(plwidget,plindex,plkey,dictkey))
                    self.nestedwidgets[key][k][-1].textChanged.connect(lambda trash, plwidget=self.nestedwidgets[key][k][-1],plindex=index,plkey='colorbar Label':self.EditPlotOptions(plwidget,plindex,plkey,None))
                    
                if k in ['symbol code']:
                    intable = d['keyID'] in self.MasterData
                    self.nestedwidgets[key][k]=[]
                    self.nestedwidgets[key][k].append(QLabel('has symbol code:'))
                    grandchild = QTreeWidgetItem(child)
                    widget.setItemWidget(grandchild,0,self.nestedwidgets[key][k][-1])
                    
                    self.nestedwidgets[key][k].append(QComboBox())
                    self.nestedwidgets[key][k][-1].addItems(['True','False'])
                    lsindex = self.nestedwidgets[key][k][-1].findText(str(d['symbol code']))
                    self.nestedwidgets[key][k][-1].setCurrentIndex(lsindex)
                    grandchild = QTreeWidgetItem(child)
                    widget.setItemWidget(grandchild,0,self.nestedwidgets[key][k][-1])
                    activate = self.nestedwidgets[key][k][-1].currentText()
                    self.nestedwidgets[key][k][-1].currentIndexChanged.connect(lambda trash, plwidget=self.nestedwidgets[key][k][-1],plindex=index,plkey=k,dictkey=key:self.handleSymbolCode(plwidget,plindex,plkey,dictkey))
                    self.nestedwidgets[key][k][-1].currentIndexChanged.connect(lambda trash, plwidget=self.nestedwidgets[key][k][-1],plindex=index,plkey=k:self.EditPlotOptions(plwidget,plindex,plkey,None))
                    if not intable:
                        self.nestedwidgets[key][k][-1].setEnabled(False)
                    
                    self.nestedwidgets[key][k].append(QLabel('symbol code header:'))
                    grandchild = QTreeWidgetItem(child)
                    widget.setItemWidget(grandchild,0,self.nestedwidgets[key][k][-1])
                    
                    self.nestedwidgets[key][k].append(QComboBox())
                    if intable:
                        self.nestedwidgets[key][k][-1].addItems(d['unique headers'])
                    else:
                        self.nestedwidgets[key][k][-1].addItems([d['symbol code header']])
                    lsindex = self.nestedwidgets[key][k][-1].findText(str(d['symbol code header']))
                    self.nestedwidgets[key][k][-1].setCurrentIndex(lsindex)
                    grandchild = QTreeWidgetItem(child)
                    widget.setItemWidget(grandchild,0,self.nestedwidgets[key][k][-1])
                    if activate == 'False':
                        self.nestedwidgets[key][k][-1].setEnabled(False)
                    if not intable:
                        self.nestedwidgets[key][k][-1].setEnabled(False)
                    self.nestedwidgets[key][k][-1].currentIndexChanged.connect(lambda trash, plwidget=self.nestedwidgets[key][k][1],plindex=index,plkey=k,dictkey=key:self.handleSymbolCode(plwidget,plindex,plkey,dictkey))
                    self.nestedwidgets[key][k][-1].currentIndexChanged.connect(lambda trash,plwidget=self.nestedwidgets[key][k][-1],plindex=index,plkey='symbol code header':self.EditPlotOptions(plwidget,plindex,plkey,None))
                    
                #Slider values for list values
#                if k in ['spacing']:
#                    self.nestedwidgets[k] = []
#                    for item in v:
#                        self.nestedwidgets[k].append(QSlider())
#                        self.nestedwidgets[k][-1].setMinimum(1)
#                        self.nestedwidgets[k][-1].setMaximum(99)
#                        self.nestedwidgets[k][-1].setValue(item)
#                        grandchild = QTreeWidgetItem(child)
#                        widget.setItemWidget(grandchild,0,self.nestedwidgets[k][-1])
#                        self.nestedwidgets[k][-1].valueChanged.connect(lambda plwidget=self.nestedwidgets[k][-1],plindex=index,plkey=k,pllistindex=len(self.nestedwidgets[k]):self.EditPlotOptions(plwidget,plindex,plkey,pllistindex))
        for i,key in enumerate(treedata):
            
            parent = QTreeWidgetItem(widget)
            parent.setText(0,key)
            parent.setFlags(parent.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)
            if isinstance(treedata[key],dict):
                includelist = includelists[i]
                walkDict(treedata[key],parent,key)
#        for i in range(2):
#            widget.resizeColumnToContents(i);
        widget.expandAll()
        widget.blockSignals(False)
        
    def handleColorbar(self,widget,index,key,dictkey):
        if self.plotList[index]['keyID'] in self.MasterData:
            if widget.currentText() == 'True':
                activated = True
            else:
                activated = False            
    #        self.plotList[-1]['color']=plcolor
    
            for i,widgets in enumerate(self.nestedwidgets[dictkey][key]):
                if not isinstance(widgets,QLabel) and widgets!=widget:
                    widgets.setEnabled(activated)
                    
                    if activated and isinstance(widgets,QComboBox):
                        nwindex = widgets.findText(widgets.currentText())
                        if nwindex < 0:
                            nwindex = 0
                        widgets.setCurrentIndex(nwindex)
                    elif activated and isinstance(widgets,QLineEdit):
                        widgets.setText(self.nestedwidgets[dictkey]['colorbar'][3].currentText())
                        print self.nestedwidgets[dictkey]['colorbar'][3].currentText()
                    elif not activated and isinstance(widgets,QComboBox):
                        widgets.setCurrentIndex(-1)
                    elif not activated and isinstance(widgets,QLineEdit):
                        widgets.setText('')
                elif isinstance(widgets,QLabel) and widgets.text() == 'color map name:':
                    colormapnameindex = i
                elif isinstance(widgets,QLabel) and widgets.text() == 'color map header:':
                    colormapheaderindex = i
            for container in ['legendcontainer','markercontainer','colorcontainer']:
                for i in reversed(range(self.nestedwidgets[dictkey][container].layout().count())): 
                    self.nestedwidgets[dictkey][container].layout().itemAt(i).widget().deleteLater()
            self.plotList[index]['color'] = []
            self.nestedwidgets[dictkey]['color']=[]
            self.plotList[index]['marker'] = []
            self.nestedwidgets[dictkey]['marker']
            self.plotList[index]['legend'] = []
            self.nestedwidgets[dictkey]['legend'] = []
            if not activated:
                self.plotList[index]['color map'] = None
                for i in range(len(self.plotList[index]['y data'])):
                    self.plotList[index]['color'].append(plotcolor[i%len(plotcolor)])
                    self.nestedwidgets[dictkey]['color'].append(QComboBox())
                    self.nestedwidgets[dictkey]['color'][i].addItems(plotcolor)
                    nwindex = self.nestedwidgets[dictkey]['color'][i].findText(plotcolor[i%len(plotcolor)])
                    self.nestedwidgets[dictkey]['color'][-1].currentIndexChanged.connect(lambda trash, plwidget=self.nestedwidgets[dictkey]['color'][-1],plindex=index,plkey='color',pllistindex=i:self.EditPlotOptions(plwidget,plindex,plkey,pllistindex))
                    self.nestedwidgets[dictkey]['color'][i].setCurrentIndex(nwindex)
                    self.plotList[index]['marker'].append(plotsymb[i%len(plotsymb)])
                    self.nestedwidgets[dictkey]['marker'].append(QComboBox())
                    self.nestedwidgets[dictkey]['marker'][i].addItems(plotsymb)
                    nwindex = self.nestedwidgets[dictkey]['marker'][i].findText(plotsymb[i%len(plotsymb)])
                    self.nestedwidgets[dictkey]['marker'][-1].currentIndexChanged.connect(lambda trash, plwidget=self.nestedwidgets[dictkey]['marker'][-1],plindex=index,plkey='marker',pllistindex=i:self.EditPlotOptions(plwidget,plindex,plkey,pllistindex))
                    self.nestedwidgets[dictkey]['marker'][i].setCurrentIndex(nwindex)
                    self.plotList[index]['legend'].append(self.plotList[index]['y axis data header'][i])
                    self.nestedwidgets[dictkey]['legend'].append(QLineEdit())
                    self.nestedwidgets[dictkey]['legend'][-1].textChanged.connect(lambda trash, plwidget=self.nestedwidgets[dictkey]['legend'][-1],plindex=index,plkey='legend',pllistindex=i:self.EditPlotOptions(plwidget,plindex,plkey,pllistindex))
                    self.nestedwidgets[dictkey]['legend'][i].setText(self.plotList[index]['y axis data header'][i])
#                    colorlayout.addWidget(self.nestedwidgets[dictkey]['color'][-1])
#                    markerlayout.addWidget(self.nestedwidgets[dictkey]['marker'][-1])
#                    legendlayout.addWidget(self.nestedwidgets[dictkey]['legend'][-1])
                    self.nestedwidgets[dictkey]['legendcontainer'].layout().addWidget(self.nestedwidgets[dictkey]['legend'][-1])
                    self.nestedwidgets[dictkey]['markercontainer'].layout().addWidget(self.nestedwidgets[dictkey]['marker'][-1])
                    self.nestedwidgets[dictkey]['colorcontainer'].layout().addWidget(self.nestedwidgets[dictkey]['color'][-1])
                
            else:
#                nwindex = self.nestedwidgets[dictkey]['symbol code'][1].findText('False')
#                self.nestedwidgets[dictkey]['symbol code'][1].setCurrentIndex(nwindex)
#                self.nestedwidgets[dictkey]['symbol code'][3].setCurrentIndex(-1)
#                self.nestedwidgets[dictkey]['symbol code'][3].setEnabled(False)
                self.plotList[index]['color map'] = plt.cm.get_cmap(self.nestedwidgets[dictkey]['colorbar'][colormapnameindex+1].currentText())
                #MIGHT HAVE TO CHANGE getORIGDATSA to export data or whatever.
                origtabledata = self.tableList[self.plotList[index]['keyID']].model().getOrigData()
                #Need to take filter funciton out of tablemodel
                origtabledata = Filter(origtabledata,self.plotList[index]['filters'])
                columndata = origtabledata[self.nestedwidgets[dictkey]['colorbar'][colormapheaderindex+1].currentText()]
                for i in range(len(self.plotList[index]['y data'])):
                    self.plotList[index]['color'].append(columndata)
                    self.nestedwidgets[dictkey]['color'].append(QComboBox())
                    self.nestedwidgets[dictkey]['color'][i].addItems(plotcolor)
                    nwindex = self.nestedwidgets[dictkey]['color'][i].findText('COLORBAR')
                    self.nestedwidgets[dictkey]['color'][-1].currentIndexChanged.connect(lambda trash, plwidget=self.nestedwidgets[dictkey]['color'][-1],plindex=index,plkey='color',pllistindex=i:self.EditPlotOptions(plwidget,plindex,plkey,pllistindex))
                    self.nestedwidgets[dictkey]['color'][i].setCurrentIndex(nwindex)
                    self.plotList[index]['marker'].append(plotsymb[i%len(plotsymb)])
                    self.nestedwidgets[dictkey]['marker'].append(QComboBox())
                    self.nestedwidgets[dictkey]['marker'][i].addItems(plotsymb)
                    nwindex = self.nestedwidgets[dictkey]['marker'][i].findText(plotsymb[i%len(plotsymb)])
                    self.nestedwidgets[dictkey]['marker'][-1].currentIndexChanged.connect(lambda trash, plwidget=self.nestedwidgets[dictkey]['marker'][-1],plindex=index,plkey='marker',pllistindex=i:self.EditPlotOptions(plwidget,plindex,plkey,pllistindex))
                    self.nestedwidgets[dictkey]['marker'][i].setCurrentIndex(nwindex)
                    self.plotList[index]['legend'].append(self.plotList[index]['y axis data header'][i])
                    self.nestedwidgets[dictkey]['legend'].append(QLineEdit())
                    self.nestedwidgets[dictkey]['legend'][-1].textChanged.connect(lambda trash, plwidget=self.nestedwidgets[dictkey]['legend'][-1],plindex=index,plkey='legend',pllistindex=i:self.EditPlotOptions(plwidget,plindex,plkey,pllistindex))
                    self.nestedwidgets[dictkey]['legend'][i].setText(self.plotList[index]['y axis data header'][i])
#                    colorlayout.addWidget(self.nestedwidgets[dictkey]['color'][-1])
#                    markerlayout.addWidget(self.nestedwidgets[dictkey]['marker'][-1])
#                    legendlayout.addWidget(self.nestedwidgets[dictkey]['legend'][-1])
                    self.nestedwidgets[dictkey]['legendcontainer'].layout().addWidget(self.nestedwidgets[dictkey]['legend'][-1])
                    self.nestedwidgets[dictkey]['markercontainer'].layout().addWidget(self.nestedwidgets[dictkey]['marker'][-1])
                    self.nestedwidgets[dictkey]['colorcontainer'].layout().addWidget(self.nestedwidgets[dictkey]['color'][-1])
                nwindex = self.nestedwidgets[dictkey]['symbol code'][1].findText('False')
                self.nestedwidgets[dictkey]['symbol code'][1].setCurrentIndex(nwindex)
                self.nestedwidgets[dictkey]['symbol code'][3].setCurrentIndex(-1)
                self.nestedwidgets[dictkey]['symbol code'][3].setEnabled(False)
                    
#            self.nestedwidgets[dictkey]['colorcontainer'].setLayout(colorlayout)
#            self.nestedwidgets[dictkey]['markercontainer'].setLayout(markerlayout)
#            self.nestedwidgets[dictkey]['legendcontainer'].setLayout(legendlayout)
#                    print self.nestedwidgets[dictkey]['color'][i].currentText()
#            self.populatePlotListOptions()
#            self.PlotOptionsTree.update()
            
    def handleSymbolCode(self,widget,index,key,dictkey):
        ply,plx = [],[]
        if self.plotList[index]['keyID'] in self.MasterData and self.plotList[index]['unique headers']:
            if widget.currentText() == 'True':
                activated = True
            else:
                activated = False            
            for i,widgets in enumerate(self.nestedwidgets[dictkey][key]):
                if not isinstance(widgets,QLabel) and widgets!=widget:
                    widgets.setEnabled(activated)
                    if activated and isinstance(widgets,QComboBox):
                        nwindex = widgets.findText(widgets.currentText())
                        if nwindex < 0:
                            nwindex = 0
                        widgets.setCurrentIndex(nwindex)
                    elif not activated and isinstance(widgets,QComboBox):
                        widgets.setCurrentIndex(-1)
                elif isinstance(widgets,QLabel) and widgets.text() == 'symbol code header:':
                    symbolcodeheaderindex = i
            origtabledata = self.tableList[self.plotList[index]['keyID']].model().getOrigData()
            origtabledata = Filter(origtabledata,self.plotList[index]['filters'])
            for container in ['legendcontainer','markercontainer','colorcontainer']:
                for i in reversed(range(self.nestedwidgets[dictkey][container].layout().count())): 
                    self.nestedwidgets[dictkey][container].layout().itemAt(i).widget().deleteLater()
            self.plotList[index]['color'] = []
            self.nestedwidgets[dictkey]['color']=[]
            self.plotList[index]['marker'] = []
            self.nestedwidgets[dictkey]['marker']
            self.plotList[index]['legend'] = []
            self.nestedwidgets[dictkey]['legend'] = []
            if not activated:
                self.plotList[index]['symbol code header'] = ''
                self.plotList[index]['y data'] = []
                self.plotList[index]['x data'] = []
                for i,header in enumerate(self.plotList[index]['y axis data header']):
                    self.plotList[index]['y data'].append(origtabledata[header])
                    self.plotList[index]['x data'].append(origtabledata[self.plotList[index]['x axis data header']])
                    self.plotList[index]['color'].append(plotcolor[i%len(plotcolor)])
                    self.nestedwidgets[dictkey]['color'].append(QComboBox())
                    self.nestedwidgets[dictkey]['color'][i].addItems(plotcolor)
                    nwindex = self.nestedwidgets[dictkey]['color'][i].findText(plotcolor[i%len(plotcolor)])
                    self.nestedwidgets[dictkey]['color'][-1].currentIndexChanged.connect(lambda trash, plwidget=self.nestedwidgets[dictkey]['color'][-1],plindex=index,plkey='color',pllistindex=i:self.EditPlotOptions(plwidget,plindex,plkey,pllistindex))
                    self.nestedwidgets[dictkey]['color'][i].setCurrentIndex(nwindex)
                    self.plotList[index]['marker'].append(plotsymb[i%len(plotsymb)])
                    self.nestedwidgets[dictkey]['marker'].append(QComboBox())
                    self.nestedwidgets[dictkey]['marker'][i].addItems(plotsymb)
                    nwindex = self.nestedwidgets[dictkey]['marker'][i].findText(plotsymb[i%len(plotsymb)])
                    self.nestedwidgets[dictkey]['marker'][-1].currentIndexChanged.connect(lambda trash, plwidget=self.nestedwidgets[dictkey]['marker'][-1],plindex=index,plkey='marker',pllistindex=i:self.EditPlotOptions(plwidget,plindex,plkey,pllistindex))
                    self.nestedwidgets[dictkey]['marker'][i].setCurrentIndex(nwindex)
                    self.plotList[index]['legend'].append(header)
                    self.nestedwidgets[dictkey]['legend'].append(QLineEdit())
                    self.nestedwidgets[dictkey]['legend'][-1].textChanged.connect(lambda trash, plwidget=self.nestedwidgets[dictkey]['legend'][-1],plindex=index,plkey='legend',pllistindex=i:self.EditPlotOptions(plwidget,plindex,plkey,pllistindex))
                    self.nestedwidgets[dictkey]['legend'][i].setText(header)
                    self.nestedwidgets[dictkey]['legendcontainer'].layout().addWidget(self.nestedwidgets[dictkey]['legend'][-1])
                    self.nestedwidgets[dictkey]['markercontainer'].layout().addWidget(self.nestedwidgets[dictkey]['marker'][-1])
                    self.nestedwidgets[dictkey]['colorcontainer'].layout().addWidget(self.nestedwidgets[dictkey]['color'][-1])
            else:
#                nwindex = self.nestedwidgets[dictkey]['colorbar'][1].findText('False')
#                self.nestedwidgets[dictkey]['colorbar'][1].setCurrentIndex(nwindex)
#                self.nestedwidgets[dictkey]['colorbar'][3].setCurrentIndex(-1)
#                self.nestedwidgets[dictkey]['colorbar'][3].setEnabled(False)
#                self.nestedwidgets[dictkey]['colorbar'][5].setCurrentIndex(-1)
#                self.nestedwidgets[dictkey]['colorbar'][5].setEnabled(False)
#                self.nestedwidgets[dictkey]['colorbar'][7].setText('')
#                self.nestedwidgets[dictkey]['colorbar'][7].setEnabled(False)
                
                self.plotList[index]['unique values'] = pd.unique(origtabledata[self.nestedwidgets[dictkey]['symbol code'][symbolcodeheaderindex+1].currentText()])
                uniquedata = origtabledata[self.nestedwidgets[dictkey]['symbol code'][symbolcodeheaderindex+1].currentText()]
                xdata = origtabledata[self.plotList[index]['x axis data header']]
                for i,header in enumerate(self.plotList[index]['y axis data header']):
#                    self.plotList[index]['color'].append(plotcolor[i%len(plotcolor)])
#                    self.nestedwidgets[dictkey]['color'].append(QComboBox())
#                    self.nestedwidgets[dictkey]['color'][i].addItems(plotcolor)
#                    nwindex = self.nestedwidgets[dictkey]['color'][i].findText(plotcolor[i%len(plotcolor)])
#                    self.nestedwidgets[dictkey]['color'][-1].currentIndexChanged.connect(lambda trash, plwidget=self.nestedwidgets[dictkey]['color'][-1],plindex=index,plkey='color',pllistindex=i:self.EditPlotOptions(plwidget,plindex,plkey,pllistindex))
#                    self.nestedwidgets[dictkey]['color'][i].setCurrentIndex(nwindex)
                    if self.plotList[index]['plot type'] not in ['Timeline']:
                        ydata = origtabledata[header]
                    elif self.plotList[index]['plot type'] == 'Timeline':
                        ydata = np.array([self.plotList[index]['Dset']+header]*xdata.size)
                    for j,val in enumerate(self.plotList[index]['unique values']):
#                        print plotcolor[(j+(i*len(self.plotList[index]['unique values'])))%len(plotcolor)]
                        self.plotList[index]['color'].append(plotcolor[(j+(i*len(self.plotList[index]['unique values'])))%len(plotcolor)])
                        self.nestedwidgets[dictkey]['color'].append(QComboBox())
                        self.nestedwidgets[dictkey]['color'][-1].addItems(plotcolor)
                        nwindex = self.nestedwidgets[dictkey]['color'][-1].findText(plotcolor[(j+(i*len(self.plotList[index]['unique values'])))%len(plotcolor)])
                        self.nestedwidgets[dictkey]['color'][-1].currentIndexChanged.connect(lambda trash, plwidget=self.nestedwidgets[dictkey]['color'][-1],plindex=index,plkey='color',pllistindex=j+(i*len(self.plotList[index]['unique values'])):self.EditPlotOptions(plwidget,plindex,plkey,pllistindex))
                        self.nestedwidgets[dictkey]['color'][-1].setCurrentIndex(nwindex)
                        self.plotList[index]['marker'].append(plotsymb[(j+(i*len(self.plotList[index]['unique values'])))%len(plotsymb)])
                        self.nestedwidgets[dictkey]['marker'].append(QComboBox())
                        self.nestedwidgets[dictkey]['marker'][-1].addItems(plotsymb)
                        nwindex = self.nestedwidgets[dictkey]['marker'][-1].findText(plotsymb[(j+(i*len(self.plotList[index]['unique values'])))%len(plotsymb)])
                        self.nestedwidgets[dictkey]['marker'][-1].currentIndexChanged.connect(lambda trash, plwidget=self.nestedwidgets[dictkey]['marker'][-1],plindex=index,plkey='marker',pllistindex=(j+(i*len(self.plotList[index]['unique values']))):self.EditPlotOptions(plwidget,plindex,plkey,pllistindex))
                        self.nestedwidgets[dictkey]['marker'][-1].setCurrentIndex(nwindex)
                        self.plotList[index]['legend'].append(str(val))
                        self.nestedwidgets[dictkey]['legend'].append(QLineEdit())
                        self.nestedwidgets[dictkey]['legend'][-1].textChanged.connect(lambda trash, plwidget=self.nestedwidgets[dictkey]['legend'][-1],plindex=index,plkey='legend',pllistindex=(j+(i*len(self.plotList[index]['unique values']))):self.EditPlotOptions(plwidget,plindex,plkey,pllistindex))
                        self.nestedwidgets[dictkey]['legend'][-1].setText(str(val))
                        self.nestedwidgets[dictkey]['legendcontainer'].layout().addWidget(self.nestedwidgets[dictkey]['legend'][-1])
                        self.nestedwidgets[dictkey]['markercontainer'].layout().addWidget(self.nestedwidgets[dictkey]['marker'][-1])
                        self.nestedwidgets[dictkey]['colorcontainer'].layout().addWidget(self.nestedwidgets[dictkey]['color'][-1])
                        idx = uniquedata == val
                        if True in idx:
                            ply.append(ydata[idx])
                            plx.append(xdata[idx])
                self.plotList[index]['y data'] = ply
                self.plotList[index]['x data'] = plx
                nwindex = self.nestedwidgets[dictkey]['colorbar'][1].findText('False')
                self.nestedwidgets[dictkey]['colorbar'][1].setCurrentIndex(nwindex)
                self.nestedwidgets[dictkey]['colorbar'][3].setCurrentIndex(-1)
                self.nestedwidgets[dictkey]['colorbar'][3].setEnabled(False)
                self.nestedwidgets[dictkey]['colorbar'][5].setCurrentIndex(-1)
                self.nestedwidgets[dictkey]['colorbar'][5].setEnabled(False)
                self.nestedwidgets[dictkey]['colorbar'][7].setText('')
                self.nestedwidgets[dictkey]['colorbar'][7].setEnabled(False)
#                print self.plotList[index]['color']
#            self.populatePlotListOptions()
#            self.PlotOptionsTree.update()
            
    def EditPlotOptions(self,widget,index,key,listindex):
        if isinstance(widget,QComboBox):
            getText = widget.currentText
        if isinstance(widget,QLineEdit):
            print 'in hereeee'
            getText = widget.text
        if isinstance(widget,QSlider):
            getText = widget.value
        if listindex != None:
            val = getText()
            if val != 'COLORBAR':
                if val == 'True':
                        val = True
                if val == 'False':
                    val = False
                self.plotList[index][key][listindex] = val
        else:
            val = getText()
            if val == 'True':
                val = True
            if val == 'False':
                val = False
            self.plotList[index][key] = val
#        print self.plotList[index]
        
    def plotListPlot(self,Save=False,Advanced=False):
        for i in range(self.PlotTree.topLevelItemCount()):
            if self.PlotTree.topLevelItem(i).isSelected():
                index = self.plotList[i]['index']
                pl = self.plotList[index]
                print pl.keys()
                fig,ax = plt.subplots()
                print pl['color map name']
                if pl['plot type'] == 'Scatter':
                    for i,ydat in enumerate(pl['y data']):
                        print pl['color'][i]
                        sc = ax.scatter(pl['x data'][i],ydat,c=pl['color'][i],cmap=pl['color map'],label=pl['legend'][i],marker=pl['marker'][i],s=pl['marker size'])
                    if pl['color map']:
                        cb = fig.colorbar(sc)
                        cb.set_label(pl['colorbar Label'])
                plt.legend().draggable()
                plt.xlabel(pl['x label'])
                plt.ylabel(pl['y label'])
                plt.title(pl['plot title'])
                plt.show()
#        self.PlotOutDir = os.path.join(os.getcwd(),'PlotTests')
#        if not os.path.isdir(self.PlotOutDir):
#            os.mkdir(self.PlotOutDir)
#        if self.PlotTree.currentItem():
#            if not self.CombineAxisChk.isChecked() and not Advanced:
#                for i in range(self.PlotTree.topLevelItemCount()):
#                    if self.PlotTree.topLevelItem(i).isSelected():
#                        pltr = Plotterator.Plotter()
#                        pltr.sub = copy.deepcopy(self.plotList[i]['sub'])
#                        pltr.fig = copy.deepcopy(self.plotList[i]['fig'])
#                        if not Save:
#                            pltr.createPlot('',PERSIST=True)
#                        else:
#                            pltr.createPlot(os.path.join(self.PlotOutDir,'test'+str(i)),SAVEPKL=True)
#            if self.CombineAxisChk.isChecked() and not Advanced:
#                pltr = {}
#                pltr['Scatter-Line'] = {}
#                pltr['Timeline'] = {}
#                pltr['Stacked'] = {}
#                pltr['Bar'] = {}
#                pltr['Pie'] = {}
#                pltr['Basemap'] = {}
#                pltr['3D Plot'] = {}
#                uniqueXAxis = self.getUniqueXAxis(pltr.keys())
#                for key in pltr.keys():
#                    if key in uniqueXAxis:
#                        for xaxis in uniqueXAxis[key]:
#                            pltr[key][xaxis] = Plotterator.Plotter()                    
#                for i in range(self.PlotTree.topLevelItemCount()):
#                    if self.PlotTree.topLevelItem(i).isSelected():
#                        ptype = self.PlotTree.topLevelItem(i).text(1)
#                        index = int(self.PlotTree.topLevelItem(i).text(5))
#                        for key in pltr.keys():
#                            for xaxis in pltr[key].keys():
#                                if ptype in key and ptype in ['Scatter','Line','Timeline','Basemap','3D Plot']:
#                                    if pltr[key][xaxis].sub and xaxis.lower() == self.plotList[i]['xaxis'].lower():
#                                        for lines in self.plotList[i]['sub'][(0,0)]['lines']:
#                                            pltr[key][xaxis].sub[(0,0)]['lines'].append(copy.deepcopy(lines))
#                                    elif xaxis.lower() in self.plotList[i]['xaxis'].lower():
#                                        pltr[key][xaxis].sub = copy.deepcopy(self.plotList[i]['sub'])
#                                        pltr[key][xaxis].fig = copy.deepcopy(self.plotList[i]['fig'])
#                                elif ptype in key and xaxis.lower() == self.plotList[i]['xaxis'].lower():
#                                    pltr[key][xaxis].sub = copy.deepcopy(self.plotList[i]['sub'])
#                                    pltr[key][xaxis].fig = copy.deepcopy(self.plotList[i]['fig'])
#                                    if not Save:
#                                        pltr[key][xaxis].createPlot('',PERSIST=True)
#                                    else:
#                                        pltr[key][xaxis].createPlot(os.path.join(self.PlotOutDir,'test'+str(i)),SAVEPKL=True)
#                                    pltr[key][xaxis] = Plotterator.Plotter()
#                for key in ['Scatter-Line','Timeline','Basemap','3D Plot']:
#                    for xaxis in pltr[key].keys():
#                        if pltr[key][xaxis].sub:
#                            if not Save:
#                                pltr[key][xaxis].createPlot('',PERSIST=True)
#                            else:
#                                pltr[key][xaxis].createPlot(os.path.join(self.PlotOutDir,'test'+key),SAVEPKL=True)
#            if Advanced:
#                self.dialog = AdvancedPlot(self.plotList)
#                self.dialog.exec_()
#                
#                pass
    
    
    def Calc(self):
        self.queue = queue.Queue()
        self.thread.append(SimpleThread(self.queue, self.addOutsideData,lf.calcPI,self,np.sqrt(2),2000000))
#        self.thread.append(Worker(lf.calcpi,self,2,2**(.25),20000))
        self.thread[-1].start()
        
    def addOutsideData(self,data):
        keyID = 'Outside/piCalc'
        data = data.val
        self.MasterData[keyID] = {'SelH':data.keys(),
                                   'AllH':data.keys(),
                                   'AddH':[],
                                   'AddData':{},
                                   'Path':'Outside',
                                   'Filename':'outside',
                                   'Grp':'picalc',
                                   'Dset':'pi',
                                   'Dsets':['pi'],
                                   'Filters':[]}
        data = pd.DataFrame(data)
        self.createOutsideTable(data,keyID)
    
    def createOutsideTable(self,data,keyID):
        md = self.MasterData[keyID]
        self.TableTab.blockSignals(True)
        headers = copy.copy(md['SelH'])
        if keyID not in self.tableIDList:
            
            self.tableWidget[keyID] = QWidget()
            self.tableLayout[keyID] = QtWidgets.QVBoxLayout(self.tableWidget[keyID])
            self.tableLayout[keyID].addWidget(QLabel(os.path.join(md['Path'],md['Grp'],md['Dset'])))
            self.tableList[keyID] = QTableView()
            self.tableLayout[keyID].addWidget(self.tableList[keyID])
            self.tableIDList.append(keyID)
            self.TableTab.addTab(self.tableWidget[keyID],md['Dset'])
        self.tableList[keyID].setModel(FieldTableModel(data,headers,self))
        self.tableList[keyID].selectionModel().selectionChanged.connect(self.initPlotOptions)
        self.addNativeHeaders()
        self.initPlotOptions()
        self.TableTab.blockSignals(False)
        self.headermenu = self.tableList[keyID].horizontalHeader()
        self.headermenu.setContextMenuPolicy(Qt.CustomContextMenu)
        self.headermenu.customContextMenuRequested.connect(self.headerPopup)
            
    def setupMergeTablesCombo(self):
        self.TableNamesMergeCombo.clear()
        index = self.TableTab.currentIndex()
        keyID = self.tableIDList[index]
        if self.TableTab.count() > 1:
            for key in self.tableIDList:
                if key != keyID:
                    self.TableNamesMergeCombo.addItem(self.MasterData[key]['Dset'])
    def populateMergeLists(self):
        self.LTCommonHeadersList.clear()
        index = self.TableTab.currentIndex()
        keyID = self.tableIDList[index]
        tableheaders = self.tableList[keyID].model().getHeaderNames()
        ## add something for getting index from label or something
        othertableheaders = self.tableList[self.tableIDList[-1]].model().getHeaderNames()
        commonheaders = set(othertableheaders).intersection(set(tableheaders))
        self.LTCommonHeadersList.addItems(commonheaders)
        
    def mergeTables(self):
        if self.LTCommonHeadersList.currentIndex():
            index = self.TableTab.currentIndex()
            keyID = self.tableIDList[index]
            md = self.MasterData[keyID]
            mdl = self.MasterData[self.tableIDList[-1]]
            newkey = keyID + self.tableIDList[-1]
            mergeheaders = [item.text() for item in self.LTCommonHeadersList.selectedItems()]
            self.MasterData[newkey] = {'SelH':copy.copy(list(set(md['SelH']).union(set(mdl['SelH'])))),
                                   'AllH':copy.copy(list(set(md['AllH']).union(set(mdl['AllH'])))),
                                   'AddH':copy.copy(list(set(md['AddH']).union(set(mdl['AddH'])))),
                                   'AddData':{},
                                   'Path':copy.copy(md['Path']+mdl['Path']),
                                   'Filename':copy.copy(md['Filename']+mdl['Filename']),
                                   'Grp':copy.copy(md['Grp']+mdl['Grp']),
                                   'Dset':copy.copy(md['Dset']+mdl['Dset']),
                                   'Dsets':copy.copy(list(set(md['Dsets']).union(set(mdl['Dsets'])))),
                                   'Filters':copy.copy(list(set(md['Filters']).union(set(mdl['Filters']))))}
            mdn = self.MasterData[newkey]
            dataleft = self.tableList[keyID].model().getOrigData()
            dataright = self.tableList[self.tableIDList[-1]].model().getOrigData()
#            mergedheadersAll = list(set(self.tableList[keyID].model().getHeaderNames()).union(set(self.tableList[self.tableIDList[-1]].model().getHeaderNames())))
            data = dataleft.merge(dataright,how='outer',on=mergeheaders)
            mergedheadersAll = list(data)
            if newkey not in self.tableIDList:
                self.tableWidget[newkey] = QWidget()
                self.tableLayout[newkey] = QtWidgets.QVBoxLayout(self.tableWidget[newkey])
                self.tableLayout[newkey].addWidget(QLabel(os.path.join(mdn['Path'],mdn['Grp'],mdn['Dset'])))
                self.tableList[newkey] = QTableView()
                self.tableLayout[newkey].addWidget(self.tableList[newkey])
                self.tableIDList.append(newkey)
                self.TableTab.addTab(self.tableWidget[newkey],mdn['Dset'])
            self.tableList[newkey].setModel(FieldTableModel(data,mergedheadersAll,self))
            self.tableList[newkey].selectionModel().selectionChanged.connect(self.initPlotOptions)
            self.addNativeHeaders()
            self.initPlotOptions()
            self.TableTab.blockSignals(False)
            self.headermenu = self.tableList[newkey].horizontalHeader()
            self.headermenu.setContextMenuPolicy(Qt.CustomContextMenu)
            self.headermenu.customContextMenuRequested.connect(self.headerPopup)
            self.TableTab.setCurrentIndex(self.TableTab.count()-1)
        return
    
    def addStatTable(self,new=False):
        if self.TableTab.count():
            index = self.TableTab.currentIndex()
            keyID = self.tableIDList[index]
            md = self.MasterData[keyID]
            if self.tableLayout[keyID].count() > 2 or new:
                try:
                    widgetToRemove = self.tableLayout[keyID].itemAt(2).widget()
                    self.tableLayout[keyID].removeWidget(widgetToRemove)
                    widgetToRemove.deleteLater()
                except:
                    pass

                data = copy.copy(self.tableList[keyID].model().getTableData())
                features = ['# of Unique Vals','Max','25%','50%','75%','Min','Mean','Std. Dev.','Most Frequent']
                allheaders = ['Features']
                theaders = self.tableList[keyID].model().getHeaderNames()
                allheaders.extend(copy.copy(theaders))
                statdat = pd.DataFrame(index=features,columns=allheaders)
                for header in theaders:
                    statdat[header][0] = len(pd.unique(data[header]))
                    if data[header].dtype.kind != 'O':
                        statdat[header][1] = data[header].max()
                        statdat[header][2] = data[header].quantile(.25)
                        statdat[header][3] = data[header].quantile(.5)
                        statdat[header][4] = data[header].quantile(.75)
                        statdat[header][5] = data[header].min()
                        statdat[header][6] = data[header].mean()
                        statdat[header][7] = data[header].std()
                    else:
                        statdat[header][1] = 'N/A'
                        statdat[header][2] = 'N/A'
                        statdat[header][3] = 'N/A'
                        statdat[header][4] = 'N/A'
                        statdat[header][5] = 'N/A'
                        statdat[header][6] = 'N/A'
                        statdat[header][7] = 'N/A'
                    statdat[header][8] = data[header].astype(str).value_counts().idxmax()
                    
                statdat['Features'] = features
                dw = QDockWidget()
                stattable = QTableView()
                dw.setWidget(stattable)
                dw.setFixedHeight(325)
                dw.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
                self.tableLayout[keyID].addWidget(dw)
                stattable.setModel(FieldTableModel(statdat,allheaders,self))
                
    def templatePlot(self,plottype,symbolCodeHeader,colorbarHeader,xaxis,yaxis,plottedheader,symbolCode,colorbarType):
#        what i need:
#        xAxisDataHeader
#        yAxisDataHeader
#        symbolCode
#        colorMapHeader
#        symboCodeHeader
        y = []
        x = []
        z = []
        ylabel = ''
        colorbarlabel = ''
        marker = []
        color = []
        label = []
        if plottype == 'Scatter':
            for header in plottedheader:
                if not symbolCode:
                    y.append(self.tableList[keyID].model().getColumnData(header))
                    x.append(self.tableList[keyID].model().getColumnData(xaxis))
                    uniquevals = [0]
                else:
                    ydata = self.tableList[keyID].model().getColumnData(header)
                    uniquevals = pd.unique(self.tableList[keyID].model().getColumnData(symbolCodeHeader))
                    uniquedata = self.tableList[keyID].model().getColumnData(symbolCodeHeader)
                    xdata = self.tableList[keyID].model().getColumnData(xaxis)
                    for i,val in enumerate(uniquevals):
                        idx = uniquedata==val
                        y.append(ydata[idx])
                        x.append(xdata[idx])
                for i,ydat in enumerate(y):
                    marker.append(plotsymb[i])
                    label.append(header)
                    if colorbarHeader and not symbolCode:
                        color.append(self.tableList[keyID].model().getColumnData(colorbarHeader))
                        cm = plt.cm.get_cmap(colorbarType)
                    else:
                        color.append(plotcolor[i])
                        cm = None
            
            self.plotList[-1] = {'xlabel':xlabel,
                                     'ylabel':ylabel,
                                     'plotTitle':title,
                                     'xdata':x,
                                     'ydata':y,
                                     'xAxisDataHeader':self.PlotXAxis.currentText(),
                                     'yAxisDataHeader':plottedheader,
                                     'symbolCode':self.SymbolCode.isChecked(),
                                     'symbolCodeHeader':self.SymbolCodeHeader.currentText(),
                                     'color':color,
                                     'colorMap':cm,
                                     'colorMapHeader':self.PlotColorBar.currentText(),
                                     'colorMapName':self.ColorBarNames.currentText(),
                                     'uniqueValues':uniquevals,
                                     'marker':marker,
                                     'markersize':markersize,
                                     'legend':label,
                                     'colorbarLabel':colorbarlabel,
                                     'keyID':keyID,
                                     'path':md['Path'],
                                     'filename':md['Filename'],
                                     'group':md['Grp'],
                                     'dset':md['Dset'],
                                     'plotType':self.PlotType.currentText()}
                
        
        return
def Filter(arraydata,procedures):
    sort = False
    OrFilt = False
    sortAD = []
    AndFilt = False
    andcheckdict = dict((akey,dict((okey,[])for okey in orkeys)) for akey in orkeys)
    sortheader = []
    orcheckdict = dict((key,[]) for key in orkeys)
    for i in range(len(procedures)):
        header = procedures[i][0]
        sortby = procedures[i][1]
        value = procedures[i][2] 
        orcheck = procedures[i][3]
        andcheck = procedures[i][4]
        orchecks = False
        andchecks = False
        dtype = arraydata[header].dtype
        if 'Order' not in sortby:
            if dtype == 'O':
                if 'Range' in sortby and ':' in value:
                    valueLower,valueUpper = value.split(':')
                    if valueLower == '':
                        valueLower = ''
                    if valueUpper == '':
                        valueUpper = ''
                elif 'Range' in sortby:
                    print ('There is no ":" in the value for the In Range filter')
                    continue
                else:
                    value = str(value).lower()
            elif dtype == 'b':
                if 'Range' in sortby and ':' in value:
                    valueLower,valueUpper = value.split(':')
                    if valueLower == '':
                        valueLower = False
                    if valueUpper == '':
                        valueUpper = True
                    try:
                        valueLower = bool(valueLower)
                        valueUpper = bool(valueUpper)
                    except:
                        print( valueLower + ' ' + valueUpper + ': One of these values cannot be of type bool')
                        continue
                elif 'Range' in sortby:
                    print( 'There is no ":" in the value for the In Range filter')
                    continue
                else:
                    try:
                        value = bool(value)
                    except:
                        print( value + ' cannot be of type bool')
                        continue
            else:
                if 'Range' in sortby and ':' in value:
                    valueLower,valueUpper = value.split(':')
                    if valueLower == '':
                        valueLower = -10000000
                    if valueUpper == '':
                        valueUpper = 10000000
                    try:
                        valueLower = float(valueLower)
                        valueUpper = float(valueUpper)
                    except:
                        print( valueLower + ' ' + valueUpper + ': One of these values cannot be of type float')
                        continue
                elif 'Range' in sortby:
                    print( 'There is no ":" in the value for the In Range filter')
                    continue
                else:
                    if 'With' in sortby:
                        try:
                            value = int(value)
                        except:
                            print( value + ' cannot be of type int')
                    else:
                        try:
                            value = float(value)
                        except:
                            print( value + ' cannot be of type float')
                            continue
        if orcheck != '':
            orchecks = True
            OrFilt = True
        if andcheck != '':
            andchecks = True
            orchecks = True
            AndFilt = True
            OrFilt = True
        if sortby == 'Less Than':
            if orchecks and not andchecks:
                orcheckdict[orcheck].append(arraydata[header]<value)
            elif orchecks and andchecks:
                andcheckdict[orcheck][andcheck].append(arraydata[header]<value)
            else:
                arraydata = arraydata[arraydata[header]<value]
        if sortby == 'Greater Than':
            if orchecks and not andchecks:
                orcheckdict[orcheck].append(arraydata[header]>value)
            elif orchecks and andchecks:
                andcheckdict[orcheck][andcheck].append(arraydata[header]>value)
            else:
                arraydata = arraydata[arraydata[header]>value]
        if sortby == 'Equal To':
            if orchecks and not andchecks:
                orcheckdict[orcheck].append(arraydata[header]==value)
            elif orchecks and andchecks:
                andcheckdict[orcheck][andcheck].append(arraydata[header]==value)
            else:
                arraydata = arraydata[arraydata[header]==value]
        if sortby == 'Not Equal To':
            if orchecks and not andchecks:
                orcheckdict[orcheck].append(arraydata[header]!=value)
            elif orchecks and andchecks:
                andcheckdict[orcheck][andcheck].append(arraydata[header]!=value)
            else:
                arraydata = arraydata[arraydata[header]!=value]
        if sortby == 'In Range':
            if orchecks and not andchecks:
                orcheckdict[orcheck].append(arraydata[header].between(valueLower,valueUpper))
            elif orchecks and andchecks:
                andcheckdict[orcheck][andcheck].append(arraydata[header].between(valueLower,valueUpper))
            else:
                arraydata = arraydata[arraydata[header].between(valueLower,valueUpper)]
        if sortby == 'Not In Range':
            if orchecks and not andchecks:
                orcheckdict[orcheck].append(~arraydata[header].between(valueLower,valueUpper))
            elif orchecks and andchecks:
                andcheckdict[orcheck][andcheck].append(~arraydata[header].between(valueLower,valueUpper))
            else:
                arraydata = arraydata[~arraydata[header].between(valueLower,valueUpper)]
        if sortby == 'Starts With':
            if orchecks and not andchecks:
                orcheckdict[orcheck].append(arraydata[header].astype(str).str.lower().str.startswith(str(value)))
            elif orchecks and andchecks:
                andcheckdict[orcheck][andcheck].append(arraydata[header].astype(str).str.lower().str.startswith(str(value)))
            else:
                arraydata = arraydata[arraydata[header].astype(str).str.lower().str.startswith(str(value))]
        if sortby == 'Does Not Start With':
            if orchecks and not andchecks:
                orcheckdict[orcheck].append(~arraydata[header].astype(str).str.lower().str.startswith(str(value)))
            elif orchecks and andchecks:
                andcheckdict[orcheck][andcheck].append(~arraydata[header].astype(str).str.lower().str.startswith(str(value)))
            else:
                arraydata = arraydata[~arraydata[header].astype(str).str.lower().str.startswith(str(value))]
        if sortby == 'Ends With':
            if orchecks and not andchecks:
                orcheckdict[orcheck].append(arraydata[header].astype(str).str.lower().str.endswith(str(value)))
            elif orchecks and andchecks:
                andcheckdict[orcheck][andcheck].append(arraydata[header].astype(str).str.lower().str.endswith(str(value)))
            else:
                arraydata = arraydata[arraydata[header].astype(str).str.lower().str.endswith(str(value))]
        if sortby == 'Does Not End With':
            if orchecks and not andchecks:
                orcheckdict[orcheck].append(~arraydata[header].astype(str).str.lower().str.endswith(str(value)))
            elif orchecks and andchecks:
                andcheckdict[orcheck][andcheck].append(~arraydata[header].astype(str).str.lower().str.endswith(str(value)))
            else:
                arraydata = arraydata[~arraydata[header].astype(str).str.lower().str.endswith(str(value))]
        if sortby == 'Contains':
            if orchecks and not andchecks:
                orcheckdict[orcheck].append(arraydata[header].astype(str).str.lower().str.contains(str(value),case=False))
            elif orchecks and not andchecks:
                andcheckdict[orcheck][andcheck].append(arraydata[header].astype(str).str.lower().str.contains(str(value),case=False))
            else:
                arraydata = arraydata[arraydata[header].astype(str).str.lower().str.contains(str(value),case=False)]
        if sortby == 'Does Not Contain':
            if orchecks and not andchecks:
                orcheckdict[orcheck].append(~arraydata[header].astype(str).str.lower().str.contains(str(value),case=False))
            elif orchecks and not andchecks:
                andcheckdict[orcheck][andcheck].append(~arraydata[header].astype(str).str.lower().str.contains(str(value),case=False))
            else:
                arraydata = arraydata[~arraydata[header].astype(str).str.lower().str.contains(str(value),case=False)]
        if sortby == 'Ascending Order':
            sort = True
            sortAD.append(True)
            sortheader.append(header)
        if sortby == 'Descending Order':
            sort = True
            sortAD.append(False)
            sortheader.append(header)
    if OrFilt and AndFilt:
        oidxs = []
        for okey in andcheckdict:
            idxs = []
            for akey in andcheckdict[okey]:
                if andcheckdict[okey][akey]:
                    idxs.append(pd.Series(np.array([True]*arraydata.shape[0])))
                    for idxa in andcheckdict[okey][akey]:
                        idxs[-1] = idxs[-1] & idxa
                    orcheckdict[okey].append(idxs[-1])
        AndFilt = False
                    
            
    if OrFilt and not AndFilt:
        idxs = pd.Series(np.array([True]*arraydata.shape[0]))
        for key in orcheckdict:
            if orcheckdict[key]:
                oridxs = pd.Series(np.array([False]*arraydata.shape[0]))
                for idxo in orcheckdict[key]:
                    oridxs = oridxs | idxo
                idxs = idxs & oridxs
        arraydata.reset_index(inplace=True, drop=True)
        arraydata = arraydata[idxs]
    if sort:
        arraydata = arraydata.sort_values(by=sortheader,ascending=sortAD)
    arraydata.reset_index(inplace=True, drop=True)
    return arraydata
        
class FieldTableModel(QAbstractTableModel):
    def __init__(self, datain={}, header=[], parent=None, *args):
        QAbstractTableModel.__init__(self, parent, *args)
        self.arraydata = copy.deepcopy(datain)
        self.DataOrig = copy.deepcopy(datain)
        self.header = header
        self.combat = np.array(np.arange(self.DataOrig[header[0]].size))
        self.parent = parent
        self.procedures = []

    def rowCount(self, parent):
        return self.arraydata.shape[0]

    def columnCount(self, parent):
        return self.arraydata.shape[1]

    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return self.header[section]
            else:
                return section

    def flags(self, index):
        return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
    
    def setData(self, index, value, role = QtCore.Qt.EditRole):
        if role == QtCore.Qt.EditRole:
            row = index.row()
            column = index.column()
            dtype = self.arraydata[self.header[column]][row].dtype.kind
            value = value.toPyObject()
            self.arraydata[self.header[column]][row] = value
            self.DataOrig[self.header[column]][self.combat[row]] = value
#            self.dataChanged.emit(self.createIndex(0, 0), self.createIndex(self.rowCount(None), self.columnCount(None)))
            self.dataChanged.emit(index, index)
            self.hideEmptyRows()
            return True
        else:
            return False

    def data(self, index, role):
        if not index.isValid():
            return None
        if role == Qt.DisplayRole:
            value = self.arraydata[self.header[index.column()]][index.row()]
            return str(value)
        
    def addColumnData(self,data,headers):
        if set(headers).issubset(self.header):
            return
        for header in headers:
            self.header.append(header)
        self.DataOrig = self.DataOrig.join(data)
        self.filterTable(self.procedures)
        
    def removeColumnData(self,header):
        if set(header).issubset(self.header):
            self.header.pop(self.header.index(header[0]))
            self.DataOrig = self.DataOrig.drop(columns=header)
        
    def removerows(self,rowlist,parent = QtCore.QModelIndex()):

        for header in self.header:
            self.arraydata[header] = np.delete(self.arraydata[header],rowlist)
            self.DataOrig[header] = np.delete(self.DataOrig[header],self.combat[rowlist])
        idx = self.combat > rowlist[0] 
        self.combat[idx] -= 1
        self.dataChanged.emit(self.createIndex(0, 0), self.createIndex(self.rowCount(0), self.columnCount(0)))
        self.hideEmptyRows()
        return
    
    def getDtype(self,header):
        return self.arraydata[header].dtype.kind
    
    def getColumnData(self,header):
        return self.arraydata[header]
    
    def getTableData(self):
        return self.arraydata
    
    def getOrigData(self):
        return self.DataOrig
    
    def getHeaderNames(self):
        return self.header
    
    def filterTable(self,procedures=[]):
        self.arraydata = copy.deepcopy(self.DataOrig)
        self.procedures = procedures
        self.arraydata = Filter(self.arraydata,self.procedures)
#        sort = False
#        OrFilt = False
#        sortAD = []
#        AndFilt = False
#        andcheckdict = dict((akey,dict((okey,[])for okey in orkeys)) for akey in orkeys)
#        sortheader = []
#        orcheckdict = dict((key,[]) for key in orkeys)
#        for i in range(len(self.procedures)):
#            header = self.procedures[i][0]
#            sortby = self.procedures[i][1]
#            value = self.procedures[i][2] 
#            orcheck = self.procedures[i][3]
#            andcheck = self.procedures[i][4]
#            orchecks = False
#            andchecks = False
#            dtype = self.arraydata[header].dtype
#            if 'Order' not in sortby:
#                if dtype == 'O':
#                    if 'Range' in sortby and ':' in value:
#                        valueLower,valueUpper = value.split(':')
#                        if valueLower == '':
#                            valueLower = ''
#                        if valueUpper == '':
#                            valueUpper = ''
#                    elif 'Range' in sortby:
#                        print ('There is no ":" in the value for the In Range filter')
#                        continue
#                    else:
#                        value = str(value).lower()
#                elif dtype == 'b':
#                    if 'Range' in sortby and ':' in value:
#                        valueLower,valueUpper = value.split(':')
#                        if valueLower == '':
#                            valueLower = False
#                        if valueUpper == '':
#                            valueUpper = True
#                        try:
#                            valueLower = bool(valueLower)
#                            valueUpper = bool(valueUpper)
#                        except:
#                            print( valueLower + ' ' + valueUpper + ': One of these values cannot be of type bool')
#                            continue
#                    elif 'Range' in sortby:
#                        print( 'There is no ":" in the value for the In Range filter')
#                        continue
#                    else:
#                        try:
#                            value = bool(value)
#                        except:
#                            print( value + ' cannot be of type bool')
#                            continue
#                else:
#                    if 'Range' in sortby and ':' in value:
#                        valueLower,valueUpper = value.split(':')
#                        if valueLower == '':
#                            valueLower = -10000000
#                        if valueUpper == '':
#                            valueUpper = 10000000
#                        try:
#                            valueLower = float(valueLower)
#                            valueUpper = float(valueUpper)
#                        except:
#                            print( valueLower + ' ' + valueUpper + ': One of these values cannot be of type float')
#                            continue
#                    elif 'Range' in sortby:
#                        print( 'There is no ":" in the value for the In Range filter')
#                        continue
#                    else:
#                        if 'With' in sortby:
#                            try:
#                                value = int(value)
#                            except:
#                                print( value + ' cannot be of type int')
#                        else:
#                            try:
#                                value = float(value)
#                            except:
#                                print( value + ' cannot be of type float')
#                                continue
#            if orcheck != '':
#                orchecks = True
#                OrFilt = True
#            if andcheck != '':
#                andchecks = True
#                orchecks = True
#                AndFilt = True
#                OrFilt = True
#            if sortby == 'Less Than':
#                if orchecks and not andchecks:
#                    orcheckdict[orcheck].append(self.arraydata[header]<value)
#                elif orchecks and andchecks:
#                    andcheckdict[orcheck][andcheck].append(self.arraydata[header]<value)
#                else:
#                    self.arraydata = self.arraydata[self.arraydata[header]<value]
#            if sortby == 'Greater Than':
#                if orchecks and not andchecks:
#                    orcheckdict[orcheck].append(self.arraydata[header]>value)
#                elif orchecks and andchecks:
#                    andcheckdict[orcheck][andcheck].append(self.arraydata[header]>value)
#                else:
#                    self.arraydata = self.arraydata[self.arraydata[header]>value]
#            if sortby == 'Equal To':
#                if orchecks and not andchecks:
#                    orcheckdict[orcheck].append(self.arraydata[header]==value)
#                elif orchecks and andchecks:
#                    andcheckdict[orcheck][andcheck].append(self.arraydata[header]==value)
#                else:
#                    self.arraydata = self.arraydata[self.arraydata[header]==value]
#            if sortby == 'Not Equal To':
#                if orchecks and not andchecks:
#                    orcheckdict[orcheck].append(self.arraydata[header]!=value)
#                elif orchecks and andchecks:
#                    andcheckdict[orcheck][andcheck].append(self.arraydata[header]!=value)
#                else:
#                    self.arraydata = self.arraydata[self.arraydata[header]!=value]
#            if sortby == 'In Range':
#                if orchecks and not andchecks:
#                    orcheckdict[orcheck].append(self.arraydata[header].between(valueLower,valueUpper))
#                elif orchecks and andchecks:
#                    andcheckdict[orcheck][andcheck].append(self.arraydata[header].between(valueLower,valueUpper))
#                else:
#                    self.arraydata = self.arraydata[self.arraydata[header].between(valueLower,valueUpper)]
#            if sortby == 'Not In Range':
#                if orchecks and not andchecks:
#                    orcheckdict[orcheck].append(~self.arraydata[header].between(valueLower,valueUpper))
#                elif orchecks and andchecks:
#                    andcheckdict[orcheck][andcheck].append(~self.arraydata[header].between(valueLower,valueUpper))
#                else:
#                    self.arraydata = self.arraydata[~self.arraydata[header].between(valueLower,valueUpper)]
#            if sortby == 'Starts With':
#                if orchecks and not andchecks:
#                    orcheckdict[orcheck].append(self.arraydata[header].astype(str).str.lower().str.startswith(str(value)))
#                elif orchecks and andchecks:
#                    andcheckdict[orcheck][andcheck].append(self.arraydata[header].astype(str).str.lower().str.startswith(str(value)))
#                else:
#                    self.arraydata = self.arraydata[self.arraydata[header].astype(str).str.lower().str.startswith(str(value))]
#            if sortby == 'Does Not Start With':
#                if orchecks and not andchecks:
#                    orcheckdict[orcheck].append(~self.arraydata[header].astype(str).str.lower().str.startswith(str(value)))
#                elif orchecks and andchecks:
#                    andcheckdict[orcheck][andcheck].append(~self.arraydata[header].astype(str).str.lower().str.startswith(str(value)))
#                else:
#                    self.arraydata = self.arraydata[~self.arraydata[header].astype(str).str.lower().str.startswith(str(value))]
#            if sortby == 'Ends With':
#                if orchecks and not andchecks:
#                    orcheckdict[orcheck].append(self.arraydata[header].astype(str).str.lower().str.endswith(str(value)))
#                elif orchecks and andchecks:
#                    andcheckdict[orcheck][andcheck].append(self.arraydata[header].astype(str).str.lower().str.endswith(str(value)))
#                else:
#                    self.arraydata = self.arraydata[self.arraydata[header].astype(str).str.lower().str.endswith(str(value))]
#            if sortby == 'Does Not End With':
#                if orchecks and not andchecks:
#                    orcheckdict[orcheck].append(~self.arraydata[header].astype(str).str.lower().str.endswith(str(value)))
#                elif orchecks and andchecks:
#                    andcheckdict[orcheck][andcheck].append(~self.arraydata[header].astype(str).str.lower().str.endswith(str(value)))
#                else:
#                    self.arraydata = self.arraydata[~self.arraydata[header].astype(str).str.lower().str.endswith(str(value))]
#            if sortby == 'Contains':
#                if orchecks and not andchecks:
#                    orcheckdict[orcheck].append(self.arraydata[header].astype(str).str.lower().str.contains(str(value),case=False))
#                elif orchecks and not andchecks:
#                    andcheckdict[orcheck][andcheck].append(self.arraydata[header].astype(str).str.lower().str.contains(str(value),case=False))
#                else:
#                    self.arraydata = self.arraydata[self.arraydata[header].astype(str).str.lower().str.contains(str(value),case=False)]
#            if sortby == 'Does Not Contain':
#                if orchecks and not andchecks:
#                    orcheckdict[orcheck].append(~self.arraydata[header].astype(str).str.lower().str.contains(str(value),case=False))
#                elif orchecks and not andchecks:
#                    andcheckdict[orcheck][andcheck].append(~self.arraydata[header].astype(str).str.lower().str.contains(str(value),case=False))
#                else:
#                    self.arraydata = self.arraydata[~self.arraydata[header].astype(str).str.lower().str.contains(str(value),case=False)]
#            if sortby == 'Ascending Order':
#                sort = True
#                sortAD.append(True)
#                sortheader.append(header)
#            if sortby == 'Descending Order':
#                sort = True
#                sortAD.append(False)
#                sortheader.append(header)
#        if OrFilt and AndFilt:
#            oidxs = []
#            for okey in andcheckdict:
#                idxs = []
#                for akey in andcheckdict[okey]:
#                    if andcheckdict[okey][akey]:
#                        idxs.append(pd.Series(np.array([True]*self.arraydata.shape[0])))
#                        for idxa in andcheckdict[okey][akey]:
#                            idxs[-1] = idxs[-1] & idxa
#                        orcheckdict[okey].append(idxs[-1])
#            AndFilt = False
#                        
#                
#        if OrFilt and not AndFilt:
#            idxs = pd.Series(np.array([True]*self.arraydata.shape[0]))
#            for key in orcheckdict:
#                if orcheckdict[key]:
#                    oridxs = pd.Series(np.array([False]*self.arraydata.shape[0]))
#                    for idxo in orcheckdict[key]:
#                        oridxs = oridxs | idxo
#                    idxs = idxs & oridxs
#            self.arraydata.reset_index(inplace=True, drop=True)
#            self.arraydata = self.arraydata[idxs]
#        if sort:
#            self.arraydata = self.arraydata.sort_values(by=sortheader,ascending=sortAD)
#        self.arraydata.reset_index(inplace=True, drop=True)
        self.dataChanged.emit(self.createIndex(0, 0), self.createIndex(self.rowCount(0), self.columnCount(0)))
        self.layoutChanged.emit()
    
    def hideEmptyRows(self):
        start = np.count_nonzero(self.combat)
        init = self.rowCount(0)
        for i in range(start,self.rowCount(0)):
            self.parent.tableView.resizeSection(i, 0)
            self.parent.tableView.setUpdatesEnabled(True)
        self.parent.tableView.verticalHeader().setDefaultSectionSize(0)
        for i in range(self.columnCount(0)):
            self.parent.tableView.resizeColumnToContents(i)
        return
    
class AdvancedPlot(QDialog):
    def __init__(self,plotlist,parent=None):
        super(AdvancedPlot,self).__init__(parent)
        uic.loadUi('AdvancedPlotOptions.ui', self)
        self.plotlist = plotlist
        self.parent = parent
        self.makeConnections()
        self.setGrid()
        self.populateList()
    def makeConnections(self):
        self.Columns.activated.connect(lambda:self.setGrid())
        self.Rows.activated.connect(lambda:self.setGrid())
        
    def populateList(self):
        for i in range(len(self.plotlist)-1):
            if self.PlotType.currentText() == self.plotlist[i]['plotType']:
                item = QTreeWidgetItem()
                item.setText(0,self.plotlist[i]['filename'])
                item.setText(1,self.plotlist[i]['plotType'])
                item.setText(2,'filler')
                item.setText(3,str(self.plotlist[i]['xaxis']))
                item.setText(4,str(self.plotlist[i]['yaxis']))
                item.setText(5,str(i))
                self.Plots.addTopLevelItem(item)
        
    def setGrid(self):
        self.axiswidgets = []
        for i in reversed(range(self.LayoutGrid.count())): 
            self.LayoutGrid.itemAt(i).widget().deleteLater()
        rowspan = 1
        colspan = 1
        rows = int(self.Rows.currentText())
        cols = int(self.Columns.currentText())
        for row in range(rows):
            self.axiswidgets.append([])
            for col in range(cols):
                self.axiswidgets[row].append(QTreeWidget())
                self.axiswidgets[row][col].headerItem().setText(0,'Filename')
                self.axiswidgets[row][col].headerItem().setText(1,'Plot Type')
                self.axiswidgets[row][col].headerItem().setText(2,'Filler')
                self.axiswidgets[row][col].headerItem().setText(3,'X Axis')
                self.axiswidgets[row][col].headerItem().setText(4,'Y Axis')
                self.axiswidgets[row][col].headerItem().setText(6,'Index')
                self.axiswidgets[row][col].setAcceptDrops(True)
                self.LayoutGrid.addWidget(self.axiswidgets[row][col],row,col,rowspan,colspan)
                
    
class TreeModel(QtCore.QAbstractItemModel):  
   def __init__(self, data, parent=None):  
        super(TreeModel, self).__init__(parent)  
        self.parents=[]  
        self.dbdata = data  
        self.rootItem = TreeItem([u"NameOfColumn"])  
        self.setupModelData(self.dbdata, self.rootItem)  
  
   def setData(self, index, value, role):  
       if index.isValid() and role == QtCore.Qt.EditRole:  
 
           prev_value = self.getValue(index)  
 
           item = index.internalPointer()  
 
           item.setData(unicode(value.toString()))  
 
           return True  
       else:  
           return False  
 
   def removeRows(self, position=0, count=1,  parent=QtCore.QModelIndex()):  
 
       node = self.nodeFromIndex(parent)  
       self.beginRemoveRows(parent, position, position + count - 1)  
       node.childItems.pop(position)  
       self.endRemoveRows()  
 
   def nodeFromIndex(self, index):  
       if index.isValid():  
           return index.internalPointer()  
       else:  
           return self.rootItem  
 
   def getValue(self, index):  
       item = index.internalPointer()  
       return item.data(index.column())  
 
   def columnCount(self, parent):  
       if parent.isValid():  
           return parent.internalPointer().columnCount()  
       else:  
           return self.rootItem.columnCount()  
 
   def data(self, index, role):  
       if not index.isValid():  
           return None  
       if role != QtCore.Qt.DisplayRole:  
           return None  
 
       item = index.internalPointer()  
       return QtCore.QVariant(item.data(index.column()))  
 
   def flags(self, index):  
       if not index.isValid():  
           return QtCore.Qt.NoItemFlags  
 
       return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable  
 
   def headerData(self, section, orientation, role):  
       if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:  
           return QtCore.QVariant(self.rootItem.data(section)[0])  
 
       return None  
 
   def index(self, row, column, parent):  
 
       if row < 0 or column < 0 or row >= self.rowCount(parent) or column >= self.columnCount(parent):  
           return QtCore.QModelIndex()  
 
       if not parent.isValid():  
           parentItem = self.rootItem  
       else:  
           parentItem = parent.internalPointer()  
 
       childItem = parentItem.child(row)  
       if childItem:  
           return self.createIndex(row, column, childItem)  
       else:  
           return QtCore.QModelIndex()  
 
   def parent(self, index):  
       if not index.isValid():  
           return QtCore.QModelIndex()  
 
       childItem = index.internalPointer()  
       parentItem = childItem.parent()  
 
       if parentItem == self.rootItem:  
           return QtCore.QModelIndex()  
 
       return self.createIndex(parentItem.row(), 0, parentItem)  
 
   def rowCount(self, parent):  
       if parent.column() > 0:  
           return 0  
 
       if not parent.isValid():  
           parentItem = self.rootItem  
       else:  
           parentItem = parent.internalPointer()  

       return parentItem.childCount()  
 
   def setupModelData(self, lines, parent):  
       ind = []  
       self.parents.append(parent)  
       ind.append(0)  
       col_numb=parent.columnCount()  
       numb = 0  
 
       for line in lines:  
           numb+=1  
           lineData=line[0]  
           self.parents[-1].appendChild(TreeItem(lineData, self.parents[-1]))  
 
           columnData = line[1]  

           self.parents.append(self.parents[-1].child(self.parents[-1].childCount() - 1))  

           for j in columnData:  
                self.parents[-1].appendChild(TreeItem(j, self.parents[-1]))  
           if len(self.parents) > 0:  
                self.parents.pop()  
    
class TreeItem(object):  
    def __init__(self, data, parent=None):  
        self.parentItem = parent  
        self.itemData = data  
        self.childItems = []  
        
    def appendChild(self, item):  
        self.childItems.append(item)  
        
    def child(self, row):  
        return self.childItems[row]  
    
    def childCount(self):  
        return len(self.childItems)  
    
    def columnCount(self):  
        return len(self.itemData)  
    
    def data(self, column):  
        try:  
            return self.itemData  
       
        except IndexError:  
            return None  
    
    def parent(self):  
        return self.parentItem  
    
    def row(self):  
        if self.parentItem:  
            return self.parentItem.childItems.index(self)  
    
        return 0  
    def setData(self, data):  
        self.itemData = data
        
        
    
class Worker(QThread):
    def __init__(self,function,parent,*args):
        super(Worker, self).__init__()
        self.parent = parent
        self.function = function
        self.args = args
        
#    def runthis(self,*args):
#        self.function(*args)
        
    def run(self):
        x = self.function(*self.args)
        if x:
            self.parent.addOutsideData(x)
        
class SimpleThread(QtCore.QThread):
    finished = QtCore.pyqtSignal(object)

    def __init__(self, queue, callback, function, parent=None, *args):
        QtCore.QThread.__init__(self, parent)      
        self.queue = queue
        self.function = function
        self.args = args
        self.finished.connect(callback)

    def run(self):
        x = self.function(*self.args)
        self.finished.emit(ResultObj(x))
 
class ResultObj(QtCore.QObject):
    def __init__(self, val):
        super(ResultObj,self).__init__()
        self.val = val
        
def main():
    app = QApplication(sys.argv)
    frame = Plotter()
    frame.show()
    retval = app.exec_()
    sys.exit(retval)


if __name__ == '__main__':
    main()