# -*- coding: utf-8 -*-
"""
Created on Fri Dec 21 16:12:00 2018

@author: Jordan
"""

"""IMPORTERATOR
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
from PyQt5 import QtSql, uic
import operator
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.qt_compat import QtCore, QtWidgets, is_pyqt5
from matplotlib.backends.backend_qt5agg import (FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure
from matplotlib import colors as mcolors
import matplotlib.patches as mpatches
import cartopy
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.io.shapereader import Reader
import time
import Queue as queue
import LongFunc as lf
import random
import cPickle as pickle
from mpl_toolkits.mplot3d import Axes3D
import FilterClass
import InternationalDateline as ID
import Plotterator as Plotterator
from collections import OrderedDict
from matplotlib.lines import Line2D
"""
#import matplotlib.font_manager as mplfm
#
#import os
#import sys
#import numpy as np
#import pandas as pd
#import h5py
#from glob import glob
#import copy
#import PyQt5.QtCore as QtCore
#import PyQt5.QtGui as QtGui
#import PyQt5.QtGui as QtWidgets
#from PyQt5.Qt import *
#from PyQt5 import QtSql
#from PyQt5.QtCore import QVariant
#from PyQt5 import QtSql, uic#, QtOpenGL
#import operator
#import matplotlib
#import matplotlib.pyplot as plt
#from matplotlib.backends.qt_compat import QtCore, QtWidgets, is_pyqt5
#from matplotlib.backends.backend_qt5agg import (FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
#from matplotlib.figure import Figure
#from matplotlib import colors as mcolors
#import matplotlib.patches as mpatches
##import geopandas as gp
#import cartopy
#import cartopy.crs as ccrs
#import cartopy.feature as cfeature
#from cartopy.io.shapereader import Reader
#import time
#import Queue as queue
#import LongFunc as lf
##import h5_traj_generator as trajgen
#import random
#import cPickle as pickle
#from mpl_toolkits.mplot3d import Axes3D
#sys.path.insert(0, 'C:\\Users\\Jordan\\Desktop\\Work Practice\\PyOpenGL_World_Py35_Qt5CarlVersion\\')
#import ota_world as otaw

#RELATIVE_LIB_PATH = os.path.join(os.path.expanduser('~'),'PyModules')
#if not hasattr(sys,'frozen'):
#    RELATIVE_LIB_PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
#    sys.path.append(RELATIVE_LIB_PATH)
#    sys.path.append(glob(os.path.join(RELATIVE_LIB_PATH,'*')))
#else:
#    RELATIVE_LIB_PATH = os.path.dirname(sys.eexecutable)


#import FilterClass
#import InternationalDateline as ID
import os
import sys
import time
if __name__ == '__main__':
    sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),'Importerator'))
    import Importerator
    exports, tup = Importerator.buildDepends('Plotter\Plotter')
    RELATIVE_LIB_PATH = Importerator.RELATIVE_LIB_PATH
    for line in exports.splitlines():
        try:
            exec line in globals(), globals()
            print(line)
        except:
            print('{} did not work.'.format(line))
    
#    import FilterClass
#    import InternationalDateline as ID
#    import Plotterator as Plotterator
#    BlueMarbleHD = os.path.join(RELATIVE_LIB_PATH,'Plotter','BlueMarbleHD.png')
#    BlueMarbleSD = os.path.join(RELATIVE_LIB_PATH,'Plotter','BlueMarbleSD.jpg')

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


BlueMarbleHD = os.path.join(RELATIVE_LIB_PATH,'Plotter','BlueMarbleHD.png')
BlueMarbleSD = os.path.join(RELATIVE_LIB_PATH,'Plotter','BlueMarbleSD.jpg')

#import Plotterator as Plotterator
#from collections import OrderedDict
#from matplotlib.lines import Line2D
plotcolor.append('COLORBAR')
TIMEFIELDS = ['ValidityTime_TALO','ScenarioTime_TALO','Time','time']
TRANSFORMS = ['Plate Carree','North Polar','EckertV','Rotated Pole','Orthographic']
ORTHOCENTERS = ['','USA']
BLUEMARBLE = ['','Blue Marble HD','Blue Marble SD']
cbartypes = ['Scatter','Timeline','Basemap','3D Plot']
zordertypes = ['Scatter','Line','Timeline','Bar','Basemap']
linestyles = ['-','--']
LinePlotMarkerNormalize = 10.
LinePlotLineWidthNormalize = 20.
BarPlotBarWidthNormalize = 80.




#spath = 'C:\Users\Jordan\Desktop'
spath = os.path.dirname(os.path.realpath(__file__))
#print RELATIVE_LIB_PATH


def BMOACorrection(lat,lon,radius_km):
    arclength = radius_km
    re = 6371.
    angle = arclength*180/(np.pi*re)
    height = 2*angle
    width = 2*angle
    return height,width

def JoinStrings(headername,lstarrays,delimeter = '-'):
    for i,array in enumerate(lstarrays):
        lstarrays[i] = array.astype(str)
    df = pd.concat(lstarrays,ignore_index=True,sort=False,axis=1).reset_index(drop=True)
    j = pd.DataFrame(columns=[headername])
    j[headername] = df[list(df)].apply(lambda x: delimeter.join(x), axis=1).reset_index(drop=True)
    return j

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
        
        
        #The new ish
        if  not os.path.isdir(os.path.join(os.path.expanduser('~'),'Phobos_Plots')):
            os.mkdir(os.path.join(os.path.expanduser('~'),'Phobos_Plots'))
        self.PlotListSaveDir.setText(os.path.join(os.path.expanduser('~'),'Phobos_Plots','*Plot-Title_TimeStamp*'))
        
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
        self.PlotListPlot.clicked.connect(lambda:self.plotListPlot(SaveOnly=False))
        self.PlotListSave.clicked.connect(lambda:self.plotListPlot(SaveOnly=True))
        self.AdvancedOptions.clicked.connect(lambda:self.plotListAdvanced())
        self.setDynamicConnections()
        self.PlotListRemoveSelected.clicked.connect(lambda:self.clearPlotListSelection())
        self.ClearPlotList.clicked.connect(lambda:self.clearPlotList())
        self.PlotTree.itemSelectionChanged.connect(lambda:self.populatePlotListOptions())
        self.PlotOptionsTree.itemExpanded.connect(lambda:self.PlotOptionsTree.resizeColumnToContents(0))
        self.PlotOptionsTree.itemExpanded.connect(lambda:self.PlotOptionsTree.resizeColumnToContents(1))
        self.optionsTabWidget.currentChanged.connect(lambda:self.initPlotOptions())
        self.PlotListSaveDirectoryButton.clicked.connect(lambda:self.updateSaveDirectory())
#        self.TableTab.currentChanged.connect(lambda:self.initPlot())
        
        
        self.JoinStrings.clicked.connect(self.joinStrings)
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
        self.indir = spath
        print self.indir
        
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
            if header in md['AllH'] and header not in md['SelH']:
                md['SelH'].append(header)
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
                types.append('DA CR')
            if set(['Lat','Lon','Radius']).issubset(hdrchk):
                self.addNativeHeadersbyHeader(['Lat','Lon','Radius'])
                types.append('DA R')
            if types == []:
                self.Alert("No Lat Lon Data found in dataset",True)
            self.GetTypeLatLon.clear()
            self.GetTypeLatLon.addItems(types)
            self.GetTypeLatLon.setCurrentIndex(-1)
    
    def tformMapper(self,name=None):
        if isinstance(self.Transform,QComboBox):
            if not name:
                text = self.Transform.currentText()
            else:
                text = name
            if text == 'Plate Carree':
                return ccrs.PlateCarree()
            if text == 'North Polar':
                return ccrs.NorthPolarStereo()
            if text == 'EckertV':
                return ccrs.EckertV()
            if text == 'Rotated Pole':
                return ccrs.RotatedPole()
            if text == 'Orthographic':
                return ccrs.Orthographic()
            
    def reverseTFormMapper(self,tformobj,Phobos=False):
        if 'PlateCarree' in str(tformobj):
            if not Phobos:
                return 'PlateCarree()'
            else:
                return 'Plate Carree'
        if 'NorthPolarStereo' in str(tformobj):
            if not Phobos:
                return 'NorthPolarStereo()'
            else:
                return 'North Polar'
        if 'EckertV' in str(tformobj):
            if not Phobos:
                return 'EckertV()'
            else:
                return 'EckertV'
        if 'RotatedPole' in str(tformobj):
            if not Phobos:
                return 'RotatedPole()'
            else:
                return 'Rotated Pole'
        if 'Orthographic' in str(tformobj):
            if not Phobos:
                return 'Orthographic()'
            else:
                return 'Orthographic'
            
    def blueMarble(self,name):
        ##GOTTA CHANGE
        if name == 'Blue Marble HD':
            return BlueMarbleHD
        elif name == 'Blue Marble SD':
            return BlueMarbleSD 
        else:
            return
            
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
                    projection = widget
                    widget.setCurrentIndex(-1)
                    widget.activated.connect(self.handleBasemap)
                    widget.activated.connect(lambda:self.initPlotOptions())
                    widget.activated.connect(lambda:self.Alert('Transform'))
                if 'OrthoCenter' in widget.objectName():
                    orthocenter = widget
                    widget.setCurrentIndex(-1)
                    widget.activated.connect(self.handleBasemap)
                    widget.activated.connect(lambda:self.updateCanvas())
                if 'ColorbarName' in widget.objectName():
                    colorbarname = widget
                    widget.setCurrentIndex(-1)
                    widget.activated.connect(lambda:self.initPlotOptions())
                    widget.activated.connect(lambda:self.Alert('Colorbarname'))
                if 'TypeLatLon' in widget.objectName():
                    latlontype = widget
                    widget.setCurrentIndex(-1)
                    widget.activated.connect(self.handleBasemap)
                    widget.activated.connect(lambda:self.initPlotOptions())
                    widget.activated.connect(lambda:self.Alert('latlon'))
                if 'ColorbarHeader' in widget.objectName():
                    colorbarheader = widget
                    widget.setCurrentIndex(-1)
                    widget.activated.connect(lambda:self.initPlotOptions())
                    widget.activated.connect(lambda:self.Alert('Colorbarheader'))
                if 'XAxis' in widget.objectName():
                    xaxiscombo = widget
                    widget.activated.connect(lambda:self.updateCanvas())
                    widget.activated.connect(lambda:self.Alert('xcombo'))
                    widget.setCurrentIndex(-1)
                if 'SymbolCode' in widget.objectName():
                    symbolcodecombo = widget
                    widget.setCurrentIndex(-1)
                    widget.activated.connect(lambda:self.initPlotOptions())
                    widget.activated.connect(lambda:self.Alert('symbolcodecombo'))
                if 'DALineStyle' in widget.objectName():
                    dalinestyle = widget
                    widget.setCurrentIndex(-1)
                    widget.activated.connect(lambda:self.updateCanvas())
                    widget.activated.connect(lambda:self.Alert('DA Linestyle'))
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
                if 'MarkerSize' in widget.objectName() and 'Label' not in widget.objectName():
                    markersize = widget
                if 'LineWidth' in widget.objectName() and 'Label' not in widget.objectName():
                    linewidth = widget
                if 'BarWidth' in widget.objectName() and 'Label' not in widget.objectName():
                    barwidth = widget
                if 'BinNum' in widget.objectName() and 'Label' not in widget.objectName():
                    binnum = widget
                if 'AlphaSize' in widget.objectName() and 'Label' not in widget.objectName():
                    alpha = widget
                widget.blockSignals(False)
            for widget in qslider:
                if 'BarWidthSlider' in widget.objectName():
                    barwidthslider = widget
                    widget.sliderMoved.connect(barwidth.setNum)
                    widget.sliderMoved.connect(lambda:self.updateCanvas())
                    widget.sliderMoved.connect(lambda:self.Alert('barwidth'))
                if 'MarkerSlider' in widget.objectName():
                    markerslider = widget
                    widget.sliderMoved.connect(markersize.setNum)
                    widget.sliderMoved.connect(lambda:self.updateCanvas())
                    widget.sliderMoved.connect(lambda:self.Alert('markerslider'))
                if 'LineSlider' in widget.objectName():
                    lineslider = widget
                    widget.sliderMoved.connect(linewidth.setNum)
                    widget.sliderMoved.connect(lambda:self.updateCanvas())
                    widget.sliderMoved.connect(lambda:self.Alert('lineslider'))
                if 'BinNumSlider' in widget.objectName():
                    binumslider = widget
                    widget.sliderMoved.connect(binnum.setNum)
                    widget.sliderMoved.connect(lambda:self.updateCanvas())
                    widget.sliderMoved.connect(lambda:self.Alert('binnum'))
#                    self.BinNumSlider = widget
                if 'AlphaSlider' in widget.objectName():
                    alphaslider = widget
                    widget.sliderMoved.connect(alpha.setNum)
                    widget.sliderMoved.connect(lambda:self.updateCanvas())
                    widget.sliderMoved.connect(lambda:self.Alert('alphaslider'))
#                    self.AlphaSlider = widget
            for widget in qcheck:
                widget.setChecked(False)
                if 'SymbolCodeCheckBox' in widget.objectName():
                    symbolcodecheck = widget
                    widget.toggled.connect(colorbarlabel.setDisabled)
                    widget.toggled.connect(colorbarheader.setDisabled)
                    widget.toggled.connect(colorbarname.setDisabled)
                    widget.toggled.connect(symbolcodecombo.setEnabled)
                    widget.toggled.connect(lambda:self.initPlotOptions())
                    widget.toggled.connect(lambda:self.Alert('symbolcodecheck'))
                if 'FillDA' in widget.objectName():
                    fillda = widget
                    widget.toggled.connect(lambda:self.updateCanvas())
                    widget.toggled.connect(lambda:self.Alert('fill da'))
#                    self.FillDA = widget
        self.StackedPlotOptions.setCurrentIndex(0)
        
    def groupVisWidget(self,widgets,hide):
        if isinstance(widgets,list):
            if hide:
                for widget in widgets:
                    widget.hide()
            elif not hide:
                for widget in widgets:
                    widget.show()
        else:
            self.Alert('Your widgets arent presented to me as a list')
        
    def orthoCenters(self,name):
        if name == 'USA':
            lat = 17.0
            lon = -46.0
            return lat,lon
        else:
            return 0,0
        
    def initPlot(self, doOption=True):
        if self.TableTab.count():
            index = self.TableTab.currentIndex()
            keyID = self.tableIDList[index]
        #Combo Init
        self.Transform = QComboBox()
        self.OrthoCenter = QComboBox()
        self.ColorbarNameCombo = QComboBox()
        self.GetTypeLatLon = QComboBox()
        self.ColorbarHeaderCombo = QComboBox()
        self.XAxisCombo = QComboBox()
        self.SymbolCodeCombo = QComboBox()
        self.DALineStyle = QComboBox()
        #Label Init
        self.MarkerSize = QLabel()
        self.LineWidth = QLabel()
        self.BarWidth = QLabel()
        self.BinNum = QLabel()
        self.alpha = QLabel()
        self.MarkerSizeLabel = QLabel()
        self.XComboLabel = QLabel()
        self.ColorBarHeaderLabel = QLabel()
        self.ColorBarLabelLabel = QLabel()
        self.BarWidthLabel = QLabel()
        self.BinNumLabel = QLabel()
        self.LatLonLabel = QLabel()
        self.ProjectionLabel = QLabel()
        self.AlphaLabel = QLabel()
        self.OrthoCenterLabel = QLabel()
        self.DALineStyleLabel = QLabel()
        #Slider Init
        self.BarWidthSlider = QSlider()
        self.MarkerSlider = QSlider()
        self.LineSlider = QSlider()
        self.BinNumSlider = QSlider()
        self.AlphaSlider = QSlider()
        #Line Edit Init
        self.ColorbarLabel = QLineEdit()
        #CheckBox Init
        self.SymbolCodeChk = QCheckBox()
        self.FillDA = QCheckBox()
        
        
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
            if 'OrthoCenter' in widget.objectName():
                self.OrthoCenter = widget
                self.OrthoCenter.clear()
                #Fix
                self.OrthoCenter.addItems(ORTHOCENTERS)
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
            if 'DALineStyle' in widget.objectName():
                self.DALineStyle = widget
                self.DALineStyle.clear()
                self.DALineStyle.addItem('')
                self.DALineStyle.addItems(linestyles)
                widget.setCurrentIndex(0)
        for widget in qlabel:
            widget.blockSignals(True)
            if 'MarkerSize' in widget.objectName() and not 'Label' in widget.objectName():
                self.MarkerSize = widget
            if 'LineWidth' in widget.objectName() and not 'Label' in widget.objectName():
                self.LineWidth = widget
            if 'BarWidth' in widget.objectName() and not 'Label' in widget.objectName():
                self.BarWidth = widget
            if 'BinNum' in widget.objectName() and not 'Label' in widget.objectName():
                self.BinNum = widget
            if 'AlphaSize' in widget.objectName() and not 'Label' in widget.objectName():
                self.alpha = widget
            if 'MarkerSizeLabel' in widget.objectName():
                self.MarkerSizeLabel = widget
            if 'XComboLabel' in widget.objectName():
                self.XComboLabel = widget
            if 'ColorBarHeaderLabel' in widget.objectName():
                self.ColorBarHeaderLabel = widget
            if 'ColorBarLabelLabel' in widget.objectName():
                self.ColorBarLabelLabel = widget
            if 'BarWidthLabel' in widget.objectName():
                self.BarWidthLabel = widget
            if 'BinNumLabel' in widget.objectName():
                self.BinNumLabel = widget
            if 'LatLonLabel' in widget.objectName():
                self.LatLonLabel = widget
            if 'ProjectionLabel' in widget.objectName():
                self.ProjectionLabel = widget
            if 'AlphaLabel' in widget.objectName():
                self.AlphaLabel = widget
            if 'OrthoCenterLabel' in widget.objectName():
                self.OrthoCenterLabel = widget
            if 'DALineStyleLabel' in widget.objectName():
                self.DALineStyleLabel = widget
            widget.blockSignals(False)
        for widget in qslider:
            if 'BarWidthSlider' in widget.objectName():
                self.BarWidthSlider = widget
            if 'MarkerSlider' in widget.objectName():
                self.MarkerSlider = widget
            if 'LineSlider' in widget.objectName():
                self.LineSlider = widget
            if 'BinNumSlider' in widget.objectName():
                self.BinNumSlider = widget
            if 'AlphaSlider' in widget.objectName():
                self.AlphaSlider = widget
        for widget in qlines:
            if 'ColorbarLabel' in widget.objectName():
                self.ColorbarLabel = widget
                widget.setText('')
            if 'BackGroundColor' in widget.objectName():
                widget.setText('#ffffff')
                palette.setColor(widget.backgroundRole(),QtGui.QColor(255,255,255))
        for widget in qcheck:
            widget.setChecked(False)
            if 'SymbolCodeCheckBox' in widget.objectName():
                self.SymbolCodeChk = widget
            if 'FillDAChk' in widget.objectName():
                self.FillDA = widget
        self.makeAxis()
        
    def makeAxis(self):
        if self.TableTab.count():
            index = self.TableTab.currentIndex()
            keyID = self.tableIDList[index]
            md = self.MasterData[keyID]
            model = self.tableList[keyID].model()
            headers = model.getHeaderNames()
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
            self._dynamic_ax = self.dynamic_canvas.figure.subplots() 
            self._dynamic_ax.figure.tight_layout()
            self._dynamic_ax.set_aspect('auto')
        elif types == 'Basemap':
            if not self.GetTypeLatLon.count():
                self.BaseMapLatLons()
            if self.TableTab.count():
                for header in headers:
                    if header in TIMEFIELDS:
                        index = self.XAxisCombo.findText(header)
                        break
                if index < 0:
                    index = 0
                self.XAxisCombo.setCurrentIndex(index)
                self._dynamic_ax = self.dynamic_canvas.figure.subplots(subplot_kw={'projection':ccrs.PlateCarree()})
                self._dynamic_ax.figure.tight_layout()
                self._dynamic_ax.set_aspect('auto')
        elif types == '3D Plot':
            if self.TableTab.count():
                for header in headers:
                    if header in TIMEFIELDS:
                        index = self.XAxisCombo.findText(header)
                        break
                if index < 0:
                    index = 0
                self.XAxisCombo.setCurrentIndex(index)
                self._dynamic_ax = Axes3D(self.dynamic_canvas.figure)
                self._dynamic_ax.figure.tight_layout()
                self._dynamic_ax.set_aspect('auto')
                if set(['PosX','PosY','PosZ']).issubset(set(md['AllH']+md['AddH'])):
                    self.addNativeHeadersbyHeader(['PosX','PosY','PosZ'])
                elif set(['X','Y','Z']).issubset(set(md['AllH']+md['AddH'])):
                    self.addNativeHeadersbyHeader(['X','Y','Z'])
                else:
                    self.Alert("No x,y,z data found in dataset",True)
                
    def initPlotOptions(self, TypeChange=True):
        #may need to change optionsTabWidget to whatever the widget is called
        if self.TableTab.count() and (self.optionsTabWidget.tabText(self.optionsTabWidget.currentIndex()) == 'Filter Options' or self.optionsTabWidget.tabText(self.optionsTabWidget.currentIndex()) == 'Plot Options'):
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
                if index < 0:
                    index = 0
                
            self.XAxisCombo.setCurrentIndex(index)
            codeName = self.SymbolCodeCombo.currentText()
            self.SymbolCodeCombo.clear()
            self.SymbolCodeCombo.addItems(uniqueheaders)
            index = self.SymbolCodeCombo.findText(codeName)
            self.SymbolCodeCombo.setCurrentIndex(index)
            self.makeAxis()
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
                self.ZLabelLabel.show()
                self.ZAxisLabel.show()
            else:
                self.ZLabelLabel.hide()
                self.ZAxisLabel.hide()
            if self.PlotType.currentText() in ['Pie','Basemap']:
                self.YLabelLabel.hide()
                self.YAxisLabel.hide()
            else:
                self.YLabelLabel.show()
                self.YAxisLabel.show()
            if self.PlotType.currentText() == 'Basemap':
                #handle all the shit
                self.handleBasemap()
                
                
            if self.PlotType.currentText() in ['Bar','Basemap','3D Plot']:
                for header in headers:
                    if header in TIMEFIELDS:
                        index = self.XAxisCombo.findText(header)
                        break
                if index < 0:
                    index = 0
                self.XAxisCombo.setCurrentIndex(index)
                self.XComboLabel.hide()
                self.XAxisCombo.hide()
            else:
                self.XAxisCombo.show()
                self.XComboLabel.show()
            if self.PlotType.currentText() in ['Pie']:
                self.XAxisCombo.setCurrentIndex(-1)
            if self.PlotType.currentText() not in ['Basemap','3D Plot','Pie']:
                if table.selectionModel().selectedColumns():
                    for i,index in enumerate(table.selectionModel().selectedColumns()):
                        if not self.SymbolCodeChk.isChecked():
                            self.addToPlotSymbolColor(headers[index.column()],'All',headers[index.column()],i)
                        else:
                            if self.SymbolCodeCombo.currentText():
                                uniquequants = pd.unique(model.getColumnData(self.SymbolCodeCombo.currentText()))
                                for j,val in enumerate(uniquequants):
                                    self.addToPlotSymbolColor(self.SymbolCodeCombo.currentText(),str(val),headers[index.column()]+' where '+self.SymbolCodeCombo.currentText()+'='+str(val),j+(i*len(uniquequants)))
            elif self.PlotType.currentText() in ['Basemap','3D Plot']:
                if not self.SymbolCodeChk.isChecked():
                    if self.PlotType.currentText() == 'Basemap':
                        self.addToPlotSymbolColor('Coordinates','All','Lat-Lon',0)
                    if self.PlotType.currentText() == '3D Plot':
                        self.addToPlotSymbolColor('Coordinates','All','X-Y-Z',0)
                else:
                    if self.SymbolCodeCombo.currentText():
                        uniquequants = pd.unique(model.getColumnData(self.SymbolCodeCombo.currentText()))
                        for j,val in enumerate(uniquequants):
                            if self.PlotType.currentText() == 'Basemap':
                                self.addToPlotSymbolColor(self.SymbolCodeCombo.currentText(),str(val),'Lat-Lon where '+self.SymbolCodeCombo.currentText()+'='+str(val),j)
                            if self.PlotType.currentText() == '3D Plot':
                                self.addToPlotSymbolColor(self.SymbolCodeCombo.currentText(),str(val),'X-Y-Z where '+self.SymbolCodeCombo.currentText()+'='+str(val),j)
            self.updateCanvas()
            self.PlotColorSymbol.blockSignals(False)
    
            
    def handleBasemap(self):
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
        self.ZLabelLabel.hide()
        self.ZAxisLabel.hide()
        #handle Bmoa/or reggie
        if 'DA' in self.GetTypeLatLon.currentText():
            self.AlphaLabel.show()
            self.AlphaSlider.show()
            self.alpha.show()
            self.FillDA.show()
            self.MarkerSize.hide()
            self.MarkerSizeLabel.hide()
            self.MarkerSlider.hide()
            self.DALineStyle.show()
            self.DALineStyleLabel.show()
            
        else:
            self.AlphaLabel.hide()
            self.AlphaSlider.hide()
            self.alpha.hide()
            self.FillDA.hide()
            self.MarkerSizeLabel.show()
            self.MarkerSlider.show()
            self.MarkerSize.show()
            self.DALineStyle.hide()
            self.DALineStyleLabel.hide()
            
        #handles orthographic black sheep
        if self.Transform.currentText() == 'Orthographic':
            self.OrthoCenter.show()
            self.OrthoCenterLabel.show()
            centlat,centlon = self.orthoCenters(self.OrthoCenter.currentText())
            self._dynamic_ax = self.dynamic_canvas.figure.subplots(subplot_kw={'projection':ccrs.Orthographic(centlon,centlat)})
        else:   
            self.OrthoCenter.setCurrentIndex(0)
            self.OrthoCenterLabel.hide()
            self.OrthoCenter.hide()
            self._dynamic_ax = self.dynamic_canvas.figure.subplots(subplot_kw={'projection':self.tformMapper()})
        self._dynamic_ax.figure.tight_layout()
        self._dynamic_ax.set_aspect('auto')
        
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
            plzAxisDataHeader = ''
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
            orthocenter = ''
            plzorder = []
            pldalinestyle = None

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
                elif ptype not in ['Basemap','Bar']:
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
                            plzorder.append(i+1)
                            sc = dax.scatter(plx[i],ydat,s = plmarkersize, c = plcolor[i], cmap = plcm, marker = plmarker[i], label = pllegends[i],zorder=plzorder[-1])
                        if ptype in ['Line']:
                            plzorder.append(i+1)
                            pllinewidth = int(self.LineWidth.text())
                            pllinestyle.append(self.plotLine[i].currentText())
                            sorteddata = pd.DataFrame({'x':plx[i],'y':ydat})
                            sorteddata.sort_values('x',inplace=True)
                            sc = dax.plot(sorteddata['x'],sorteddata['y'],ms = plmarkersize/LinePlotMarkerNormalize, color = plcolor[i], marker = plmarker[i],label = pllegends[i],linestyle = pllinestyle[i], linewidth = pllinewidth/LinePlotLineWidthNormalize,zorder=plzorder[-1])
                    if ptype in ['Stacked']:
                        plzorder.append(1)
                        ply = [np.row_stack(ply)]
                        sc = dax.stackplot(plx[0],ply[0],colors=[colorss for colorss in plcolor],labels=[labelss for labelss in pllegends],zorder=plzorder[-1])
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
                        self.BinNumLabel.show()
                        self.BinNum.show()
                        self.BinNumSlider.show()
                        bins = np.linspace(x.min(),x.max(),plbinnum+1)
                        y = pd.cut(x,bins)
                        plx = y.value_counts().sort_index()
                        plcolor = cmap(np.linspace(0.,1.,plbinnum))
                    else:
                        self.BinNumLabel.hide()
                        self.BinNum.hide()
                        self.BinNumSlider.hide()
                        plbinnum = None
                        u = len(pd.unique(x))
                        plcolor = cmap(np.linspace(0.,1.,u))
                        plx = x.value_counts().sort_index()
                    pllegends = map(str,plx.index.tolist())
                    plxAxisDataHeader = self.XAxisCombo.currentText()
                    plzorder.append(1)
                    sc = dax.pie(plx,autopct = '%.2f%%',colors=plcolor)
                    if not self.HideLegend.isChecked():
                        dax.figure.legend(pllegends,prop=mplfm.FontProperties(size=6),loc='best',ncol=4).draggable()

                if ptype =='Bar':
                    xheads = []
                    if self.YAxisLabel.text():
                        plylabel = self.YAxisLabel.text()
                    else:
                        plylabel = 'Number Of Occurences'
                    
                    for i,index in enumerate(table.selectionModel().selectedColumns()):
                        x = model.getColumnData(headers[index.column()])
                        plplottedheaders.append(headers[index.column()])
                        if len(pd.unique(x)) < 50:
                            plx.append(x)
                            plspacing.append(np.arange(len(pd.unique(x))))
                        else:
                            self.Alert("Too many unique values in "+str(headers[index.column()]),True)
                            return
                        xheads.append(headers[index.column()])
                    if self.XAxisLabel.text():
                        plxlabel = self.XAxisLabel.text()
                    else:
                        plxlabel = '/'.join(xheads)
                    plxAxisDataHeader = plxlabel
                    if plx:
                        plbarwidth = float(self.BarWidth.text())/len(plx)
                    else:
                        plbarwidth = 0
                    ticklabels = []
                    for i,ydat in enumerate(plx):
                        item = self.PlotColorSymbol.topLevelItem(i)
                        pllegends.append(item.text(4))
                        plcolor.append(self.plotColor[i].currentText())
                        if ydat.dtype.kind =='f':
                            ticklabels.append([str(round(float(val),2)) for val in ydat.value_counts().index])
                        else:
                            ticklabels.append(ydat.value_counts().index)
                        plzorder.append(i+1)
                        sc = dax.bar(plspacing[i] + i*plbarwidth, ydat.value_counts(),plbarwidth*.8,color = plcolor[i],label=pllegends[i],zorder=plzorder[-1])    
                    if len(plx):
                        dax.set_xticks(np.concatenate([space + i*plbarwidth for i,space in enumerate(plspacing)]))
                        dax.set_xticklabels(np.concatenate([tick for tick in ticklabels]))
                        dax.set_aspect('auto')
                    
                if ptype in ['Basemap']:
                    lltext = self.GetTypeLatLon.currentText()
                    if lltext:
                        if lltext == 'Lat/Lon':
                            Lat = 'Lat'
                            Lon = 'Lon'
                            self.ColorBarHeaderLabel.show()
                            self.ColorBarLabelLabel.show()
                            self.ColorbarHeaderCombo.show()
                            self.ColorbarNameCombo.show()
                            self.ColorbarLabel.show()
                        elif lltext == 'Impact Lat/Lon':
                            Lat = 'ImpactLat'
                            Lon = 'ImpactLon'
                            self.ColorBarHeaderLabel.show()
                            self.ColorBarLabelLabel.show()
                            self.ColorbarHeaderCombo.show()
                            self.ColorbarNameCombo.show()
                            self.ColorbarLabel.show()
                        elif lltext == 'impact Lat/Lon':
                            Lat = 'impactLat'
                            Lon = 'impactLon'
                            self.ColorBarHeaderLabel.show()
                            self.ColorBarLabelLabel.show()
                            self.ColorbarHeaderCombo.show()
                            self.ColorbarNameCombo.show()
                            self.ColorbarLabel.show()
                        elif lltext == 'Launch Lat/Lon':
                            Lat = 'LaunchLat'
                            Lon = 'LaunchLon'
                            self.ColorBarHeaderLabel.show()
                            self.ColorBarLabelLabel.show()
                            self.ColorbarHeaderCombo.show()
                            self.ColorbarNameCombo.show()
                            self.ColorbarLabel.show()
                        elif lltext == 'launch Lat/Lon':
                            Lat = 'launchLat'
                            Lon = 'launchLon'
                            self.ColorBarHeaderLabel.show()
                            self.ColorBarLabelLabel.show()
                            self.ColorbarHeaderCombo.show()
                            self.ColorbarNameCombo.show()
                            self.ColorbarLabel.show()
                        elif lltext == 'DA CR':
                            Lat = 'Lat'
                            Lon = 'Lon'
                            Radius = 'Circle_Radius'
                            plotBmoa = True
                            self.ColorBarHeaderLabel.hide()
                            self.ColorBarLabelLabel.hide()
                            self.ColorbarHeaderCombo.hide()
                            self.ColorbarNameCombo.hide()
                            self.ColorbarLabel.hide()
                        elif lltext == 'DA R':
                            Lat = 'Lat'
                            Lon = 'Lon'
                            Radius = 'Radius'
                            plotBmoa = True
                            self.ColorBarHeaderLabel.hide()
                            self.ColorBarLabelLabel.hide()
                            self.ColorbarHeaderCombo.hide()
                            self.ColorbarNameCombo.hide()
                            self.ColorbarLabel.hide()
                        #Fix for ellipses
                    else:
                        return
#                    if 'DA' in lltext:
#                        self.AlphaLabel.show()
#                        self.AlphaSlider.show()
#                        self.FillDA.show()
#                    else:
#                        self.AlphaLabel.hide()
#                        self.AlphaSlider.hide()
#                        self.FillDA.hide()
                    if plotBmoa:
                        bmoaradii = model.getColumnData(Radius)
                        plradii.append(bmoaradii)
                        plalpha = float(self.alpha.text())
                        plfillDA = self.FillDA.isChecked()
                        pldalinestyle = self.DALineStyle.currentText()
                        if not pldalinestyle:
                            pldalinestyle = None
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
                    plplottedheaders.append(Lat)
                    orthocenter = self.BasemapOrthoCenter.currentText()
                    plmarkersize = int(self.MarkerSize.text())
                    #CHECK
                    plprojection = self.tformMapper()
#                    dax.add_feature(COUNTRY_BOUNDS)    
                    dax.add_feature(cfeature.BORDERS)
                    dax.add_feature(cfeature.LAND)
                    dax.add_feature(cfeature.COASTLINE)
                    dax.add_feature(cfeature.OCEAN)
                    handles = []
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
                            plzorder.append(i+1)
                            sc = dax.scatter(plx[i],ydat,s = plmarkersize, c = plcolor[i], cmap = plcm, marker = plmarker[i], label = pllegends[i], transform = ccrs.PlateCarree(),zorder=plzorder[-1])
                        elif plotBmoa:
                            plzorder.append(i+1)
                            for j,r in enumerate(plradii[i]):
                                if r > 0:
                                    lats,lons = ID.circleLatLons(ply[i][j],plx[i][j],r)
                                    lats,lons = ID.handle_InternationalDateline(lats,lons)
                                else:
                                    lats,lons = ID.handle_InternationalDateline(ply[i][j],plx[i][j])
                                for ii in range(len(lats)):
                                    dax.add_patch(mpatches.Polygon(xy=np.array([lons[ii],lats[ii]]).T,closed = True,fill = plfillDA,color=plcolor[i],alpha=plalpha/100.,transform=ccrs.PlateCarree(),ls=pldalinestyle,zorder=plzorder[-1]))
                            if not self.HideLegend.isChecked():
                                handles.append(Line2D([0],[0],color=plcolor[i]))
                    if not self.HideLegend.isChecked() and plotBmoa:
                        dax.figure.legend(handles=handles,labels = pllegends,prop=mplfm.FontProperties(size=6),loc='best',ncol=4).draggable()
                    plxAxisDataHeader = Lon
                    if self.ColorbarHeaderCombo.currentText() and not self.SymbolCodeChk.isChecked() and not plotBmoa:
                        self.colorbar = dax.figure.colorbar(sc)
                        if self.ColorbarLabel.text():
                            plcolorbarlabel = self.ColorbarLabel.text()
                        else:
                            plcolorbarlabel = self.ColorbarHeaderCombo.currentText()
                        self.colorbar.set_label(plcolorbarlabel)
#                    dax.set_adjustable('datalim')
                    dax.set_aspect('equal')
                    dax.set_global()
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
                    else:
                        return
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
                    plplottedheaders.append(posy)
                    plzAxisDataHeader = posz
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
                        plzorder.append(i+1)
                        sc = dax.scatter(plx[i],ply[i],plz[i],zdir='z',s=plmarkersize,c=plcolor[i],cmap=plcm,marker=plmarker[i],label=pllegends[i])
                    if self.ColorbarHeaderCombo.currentText() and not self.SymbolCodeChk.isChecked():
                        self.colorbar = dax.figure.colorbar(sc)
                        if self.ColorbarLabel.text():
                            plcolorbarlabel = self.ColorbarLabel.text()
                        else:
                            plcolorbarlabel = self.ColorbarHeaderCombo.currentText()
                        self.colorbar.set_label(plcolorbarlabel)
                    dax.set_zlabel(plzlabel)
                    plxAxisDataHeader = posx

                if not self.HideLegend.isChecked() and ptype != 'Pie' and not plotBmoa:
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
                    self.plotList[-1]['z axis data header']=plzAxisDataHeader
                    self.plotList[-1]['symbol code']=self.SymbolCodeChk.isChecked()
                    self.plotList[-1]['symbol code header']=self.SymbolCodeCombo.currentText()
                    self.plotList[-1]['color']=plcolor
                    self.plotList[-1]['color map']=plcm
                    self.plotList[-1]['colorbar']=addedcolorbar
                    self.plotList[-1]['color map header']=self.ColorbarHeaderCombo.currentText()
                    self.plotList[-1]['color map name']=self.ColorbarNameCombo.currentText()
                    self.plotList[-1]['alpha']=plalpha
                    self.plotList[-1]['fill DA']=plfillDA
                    self.plotList[-1]['DA line style'] = pldalinestyle
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
                    self.plotList[-1]['index']=len(self.plotList)-1
                    self.plotList[-1]['projection']=plprojection
                    self.plotList[-1]['orthographic center'] = orthocenter
                    self.plotList[-1]['filters']=self.MasterData[keyID]['Filters']
                    self.plotList[-1]['non string headers']=plnsheaders
                    self.plotList[-1]['unique headers']=pluniqueheaders
                    self.plotList[-1]['z order']=plzorder
                    self.plotList[-1]['figure background color'] = self.FigureBackGroundColor.text()
                    self.plotList[-1]['axis background color'] = self.AxisBackGroundColor.text()

    
    def addToPlotList(self,addtomaster=True):
        if self.TableTab.count():
            index = self.TableTab.currentIndex()
            keyID = self.tableIDList[index]
            md = self.MasterData[keyID]
            pl = self.plotList[-1]
            if pl and len(pl['x data']):
                if addtomaster:
                    md['PlotList'].append(pl)
                item = QTreeWidgetItem()
                item.setText(0,pl['filename'])
                item.setText(1,pl['plot type'])
                item.setText(2,pl['plot title'])
                item.setText(3,str(pl['x axis data header']))
                item.setText(4,str(pl['y axis data header']))
                item.setText(5,str(pl['index']))
                item.setText(6,str(pl['x axis data header']))
                self.PlotTree.addTopLevelItem(item)
                self.plotList.append(OrderedDict())
                self.tableList[keyID].clearSelection()
                self.initPlot()
                self.initPlotOptions()
                return
    
            
    def clearPlotListSelection(self):
        for i in range(self.PlotTree.topLevelItemCount()-1,-1,-1):
            if self.PlotTree.topLevelItem(i).isSelected():
                item = self.PlotTree.topLevelItem(i)
                index = int(item.text(5))
                for key in self.MasterData:
                    for j,pl in enumerate(self.MasterData[key]['PlotList']):
                        if pl:
                            if index == pl['index']:
                                self.MasterData[key]['PlotList'].pop(j)
                self.plotList.pop(index)
        self.PlotTree.clear()
        for i in range(len(self.plotList)-1):
            pl = self.plotList[i]
            pl['index'] = i
            item = QTreeWidgetItem()
            item.setText(0,pl['filename'])
            item.setText(1,pl['plot type'])
            item.setText(2,pl['plot title'])
            item.setText(3,str(pl['x axis data header']))
            item.setText(4,str(pl['y axis data header']))
            item.setText(5,str(pl['index']))
            item.setText(6,str(pl['x axis data header']))
            self.PlotTree.addTopLevelItem(item)
        
            
        return
    
    def clearPlotList(self):
        self.PlotTree.clear()
        self.plotList = [OrderedDict()]
        for key in self.MasterData:
            self.MasterData[key]['PlotList'] = []
    
    def populatePlotListOptions(self):
        self.includelists = []
        self.dictionary = OrderedDict()
        for i in range(self.PlotTree.topLevelItemCount()):
            if self.PlotTree.topLevelItem(i).isSelected():
                includelist = []
                self.dictionary['Plot List Index:'+str(self.plotList[i]['index'])] = OrderedDict(self.plotList[i].items())
                if self.plotList[i]['plot type'] == 'Scatter':
                    includelist.extend(['plot title','x label','y label','marker size','marker','symbol code','color','colorbar','legend','z order','figure background color','axis background color'])
                if self.plotList[i]['plot type'] == 'Line':
                    includelist.extend(['plot title','x label','y label','marker size','marker','color','legend','line style','line width','z order','figure background color','axis background color'])
                if self.plotList[i]['plot type'] == 'Timeline':
                    includelist.extend(['plot title','x label','y label','marker size','marker','symbol code','color','colorbar','legend','figure background color','axis background color'])
                if self.plotList[i]['plot type'] == 'Stacked':
                    includelist.extend(['plot title','x label','y label','color','legend','figure background color','axis background color'])
                if self.plotList[i]['plot type'] == 'Bar':
                    #Add bar width and spacing? Not if i can help it
                    includelist.extend(['plot title','x label','y label','color','legend','figure background color','axis background color'])
                if self.plotList[i]['plot type'] == 'Pie':
                    includelist.extend(['plot title','x label','bin num','legend','figure background color','axis background color'])
                if self.plotList[i]['plot type'] == 'Basemap':
                    includelist.extend(['plot title','x label','y label','marker size','marker','symbol code','color','colorbar','legend','projection','alpha','fill DA','orthographic center','blue marble','z order','figure background color','axis background color','DA line style']) 
                if self.plotList[i]['plot type'] == '3D Plot':
                    includelist.extend(['plot title','x label','y label','z label','marker size','marker','symbol code','color','colorbar','legend','z order','figure background color','axis background color'])
                    
                self.includelists.append(includelist)
        self.setupTreeWidget(self.PlotOptionsTree,self.dictionary,self.includelists)
                
    def plotListAdvanced(self):
        self.plotListPlot(Advanced=True)
    ### TREE WIDGET STUFF
    def setupTreeWidget(self,widget,treedata,includelists):
        treedata = OrderedDict(treedata.items())
        self.PlotOptionsTree.clear()
        widget.blockSignals(True)
        self.nestedwidgets = {k:{} for k in treedata.keys()}
        for k in treedata.keys():
            self.nestedwidgets[k]['megacontainer'] = QWidget()
        def walkDict(d,parent,key):
            d = OrderedDict(d)
            index = int(key.split(':')[-1])
            for k, v in d.iteritems():
                if k not in includelist:
                    continue
                if not isinstance(k,str):
                    k = str(k)
                    
                if k not in ['legend','color','marker','line style','z order']:
                    child = QTreeWidgetItem(parent)
                    child.setText(0,k)
                if isinstance(v, dict):
                    v = walkDict(v,child,key)
                #Line edit for single values
                if k in ['x label','y label','z label','plot title']:
                    self.nestedwidgets[key][k] = QLineEdit(v)
                    grandchild = QTreeWidgetItem(child)
                    widget.setItemWidget(grandchild,0,self.nestedwidgets[key][k])
                    self.nestedwidgets[key][k].textChanged.connect(lambda trash, plwidget=self.nestedwidgets[key][k],plindex=index,plkey=k:self.EditPlotOptions(plwidget,plindex,plkey,None))
                if k in ['figure background color','axis background color']:
                    ColorWidget = QWidget()
                    self.nestedwidgets[key][k] = []
                    Layout = QHBoxLayout()
                    self.nestedwidgets[key][k].append(QPushButton(k))
                    self.nestedwidgets[key][k].append(QLineEdit(v))
                    self.nestedwidgets[key][k][0].clicked.connect(lambda trash, plwidget = self.nestedwidgets[key][k][1]:self.colorPicker(plwidget))
                    self.nestedwidgets[key][k][1].textChanged.connect(lambda trash,plwidget=self.nestedwidgets[key][k][1],plindex=index,plkey=k:self.EditPlotOptions(plwidget,plindex,plkey,None))
                    self.nestedwidgets[key][k][1].setReadOnly(True)
                    Layout.addWidget(self.nestedwidgets[key][k][0])
                    Layout.addWidget(self.nestedwidgets[key][k][1])
                    ColorWidget.setLayout(Layout)
                    grandchild = QTreeWidgetItem(child)
                    widget.setItemWidget(grandchild,0,ColorWidget)
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
                    if not d['bmoa']:
                        self.nestedwidgets[key][k][-1].setEnabled(False)
                if k in ['line style']:
                    self.nestedwidgets[key][k] = []
                    for i,item in enumerate(v):
                        self.nestedwidgets[key][k].append(QComboBox())
                        self.nestedwidgets[key][k][-1].clear()
                        self.nestedwidgets[key][k][-1].addItems(linestyles)
                        lsindex = self.nestedwidgets[key][k][-1].findText(str(item))
                        self.nestedwidgets[key][k][-1].setCurrentIndex(lsindex)
                        self.nestedwidgets[key][k][-1].currentIndexChanged.connect(lambda trash, plwidget=self.nestedwidgets[key][k][-1],plindex=index,plkey=k,pllistindex=i:self.EditPlotOptions(plwidget,plindex,plkey,pllistindex))
                if k in ['DA line style']:
                    self.nestedwidgets[key][k] = []
                    self.nestedwidgets[key][k].append(QComboBox())
                    self.nestedwidgets[key][k][-1].clear()
                    self.nestedwidgets[key][k][-1].addItems(linestyles)
                    lsindex = self.nestedwidgets[key][k][-1].findText(str(v))
                    self.nestedwidgets[key][k][-1].setCurrentIndex(lsindex)
                    self.nestedwidgets[key][k][-1].currentIndexChanged.connect(lambda trash, plwidget=self.nestedwidgets[key][k][-1],plindex=index,plkey=k:self.EditPlotOptions(plwidget,plindex,plkey,None))
                    grandchild = QTreeWidgetItem(child)
                    widget.setItemWidget(grandchild,0,self.nestedwidgets[key][k][-1])
                    if not d['bmoa']:
                        self.nestedwidgets[key][k][-1].setEnabled(False)
                if k in ['marker','color']:
                    self.nestedwidgets[key][k] = []
                    for i,item in enumerate(v):
                        self.nestedwidgets[key][k].append(QComboBox())
                        self.nestedwidgets[key][k][-1].clear()
                        if k == 'marker':
                            self.nestedwidgets[key][k][-1].addItems(plotsymb)
                        if k == 'color':
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
                        self.nestedwidgets[key][k][-1].currentIndexChanged.connect(lambda trash, plwidget=self.nestedwidgets[key][k][-1],plindex=index,plkey=k,pllistindex=i:self.EditPlotOptions(plwidget,plindex,plkey,pllistindex))
                #Line edit for list values
                if k in ['legend']:
                    self.nestedwidgets[key][k] = []
                    for i,item in enumerate(v):
                        self.nestedwidgets[key][k].append(QLineEdit(item))
                        self.nestedwidgets[key][k][-1].textChanged.connect(lambda trash, plwidget=self.nestedwidgets[key][k][-1],plindex=index,plkey=k,pllistindex=i:self.EditPlotOptions(plwidget,plindex,plkey,pllistindex))
                #Z order stuff
                if k in ['z order']:
                    self.nestedwidgets[key][k] = []
                    for i,item in enumerate(v):
                        self.nestedwidgets[key][k].append(QComboBox())
                        self.nestedwidgets[key][k][-1].clear()
                        self.nestedwidgets[key][k][-1].addItems(map(str,np.arange(1,len(v)+1,1)))
                        lsindex = self.nestedwidgets[key][k][-1].findText(str(item))
                        self.nestedwidgets[key][k][-1].setCurrentIndex(lsindex)
                        self.nestedwidgets[key][k][-1].currentIndexChanged.connect(lambda trash, plwidget=self.nestedwidgets[key][k][-1],plindex=index,plkey=k,pllistindex=i:self.EditPlotOptions(plwidget,plindex,plkey,pllistindex))
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
                    if not intable and self.nestedwidgets[key][k][-1].currentText()=='False':
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
                if k in ['projection']:
                    self.nestedwidgets[key][k] = []
                    self.nestedwidgets[key][k].append(QComboBox())
                    self.nestedwidgets[key][k][-1].addItems(TRANSFORMS)
                    lsindex = self.nestedwidgets[key][k][-1].findText(self.reverseTFormMapper(v,True))
                    self.nestedwidgets[key][k][-1].setCurrentIndex(lsindex)
                    self.nestedwidgets[key][k][-1].currentIndexChanged.connect(lambda trash, plwidget=self.nestedwidgets[key][k][-1],plindex=index,plkey=k:self.EditPlotOptions(plwidget,plindex,plkey,None))
                    grandchild = QTreeWidgetItem(child)
                    widget.setItemWidget(grandchild,0,self.nestedwidgets[key][k][-1])
                if k in ['orthographic center']:
                    self.nestedwidgets[key][k] = []
                    self.nestedwidgets[key][k].append(QComboBox())
                    self.nestedwidgets[key][k][-1].addItems(ORTHOCENTERS)
                    lsindex = self.nestedwidgets[key][k][-1].findText(v)
                    self.nestedwidgets[key][k][-1].setCurrentIndex(lsindex)
                    self.nestedwidgets[key][k][-1].currentIndexChanged.connect(lambda trash, plwidget=self.nestedwidgets[key][k][-1],plindex=index,plkey=k:self.EditPlotOptions(plwidget,plindex,plkey,None))
                    grandchild = QTreeWidgetItem(child)
                    widget.setItemWidget(grandchild,0,self.nestedwidgets[key][k][-1])
                #Slider values for one offs
                if k in ['marker size','bin num','line width','bar width','alpha']:
                    intable = d['keyID'] in self.MasterData
                    self.nestedwidgets[key][k] = []
                    self.nestedwidgets[key][k].append(QWidget())
                    mylayout = QHBoxLayout()
                    mylayout.addWidget(QLabel('Value:'))
                    mylayout.addWidget(QLabel(str(v)))
                    self.nestedwidgets[key][k][-1].setLayout(mylayout)
                    grandchild = QTreeWidgetItem(child)
                    widget.setItemWidget(grandchild,0,self.nestedwidgets[key][k][-1])
                    self.nestedwidgets[key][k].append(QSlider(Qt.Horizontal))
                    self.nestedwidgets[key][k][-1].setMinimum(1)
                    self.nestedwidgets[key][k][-1].setMaximum(99)
                    if v:
                        self.nestedwidgets[key][k][-1].setValue(int(v))
                    else:
                        self.nestedwidgets[key][k][-1].setValue(0)
                    grandchild = QTreeWidgetItem(child)
                    widget.setItemWidget(grandchild,0,self.nestedwidgets[key][k][-1])
                    if k in ['bin num']:
                        if not d['bin num'] or not intable:
                            self.nestedwidgets[key][k][-1].setEnabled(False)
                        self.nestedwidgets[key][k][-1].valueChanged.connect(lambda trash, plwidget=self.nestedwidgets[key][k][-1],plindex=index,plkey=k,dictkey=key:self.handleBinNumber(plwidget,plindex,plkey,dictkey))
                    self.nestedwidgets[key][k][-1].valueChanged.connect(lambda trash,plwidget=self.nestedwidgets[key][k][-1],plindex=index,plkey=k:self.EditPlotOptions(plwidget,plindex,plkey,None))
                    self.nestedwidgets[key][k][-1].valueChanged.connect(lambda val,plwidget=self.nestedwidgets[key][k][0].layout().itemAt(1).widget():plwidget.setText(str(val)))
                    if k == 'alpha' and not d['bmoa']:
                        self.nestedwidgets[key][k][-1].setEnabled(False)
            mylayout = QGridLayout()
            child = QTreeWidgetItem(parent)
            childname = ', '
            cname = []
            for i in range(len(self.nestedwidgets[key]['legend'])):
                j = 0
                if 'color' in self.nestedwidgets[key]:
                    if i == 0:
                        cname.append('colors')
                        mylayout.addWidget(QLabel('Colors'),0,j,1,1)
                    mylayout.addWidget(self.nestedwidgets[key]['color'][i],i+1,j,1,1)   
                    j+=1
                if 'marker' in self.nestedwidgets[key]:
                    if i == 0:
                        cname.append('markers')
                        mylayout.addWidget(QLabel('Marker'),0,j,1,1)
                    mylayout.addWidget(self.nestedwidgets[key]['marker'][i],i+1,j,1,1)
                    j+=1
                if 'line style' in self.nestedwidgets[key]:
                    if i == 0:
                        cname.append('line styles')
                        mylayout.addWidget(QLabel('Line Style'),0,j,1,1)
                    mylayout.addWidget(self.nestedwidgets[key]['line style'][i],i+1,j,1,1)
                    j+=1
                if 'legend' in self.nestedwidgets[key]:
                    if i == 0:
                        cname.append('legend names')
                        mylayout.addWidget(QLabel('Legend Names'),0,j,1,1)
                    mylayout.addWidget(self.nestedwidgets[key]['legend'][i],i+1,j,1,1)
                    j+=1
                if 'z order' in self.nestedwidgets[key]:
                    if i == 0:
                        cname.append('z order')
                        mylayout.addWidget(QLabel('Z Order'),0,j,1,1)
                    mylayout.addWidget(self.nestedwidgets[key]['z order'][i],i+1,j,1,1)
                    j+=1
            childname = childname.join(cname)
            cname = childname.rsplit(',',1)
            childname = ' and'.join(cname)
            child.setText(0,childname)
            self.nestedwidgets[key]['megacontainer'].setLayout(mylayout)
            grandchild = QTreeWidgetItem(child)
            widget.setItemWidget(grandchild,0,self.nestedwidgets[key]['megacontainer'])
            
            if d['plot type'] == 'Basemap':
                child = QTreeWidgetItem(parent)
                child.setText(0,'blue marble')
                self.BlueMarble = QComboBox()
                self.BlueMarble.addItems(BLUEMARBLE)
                self.BlueMarble.setCurrentIndex(0)
                grandchild = QTreeWidgetItem(child)
                widget.setItemWidget(grandchild,0,self.BlueMarble)
        for i,key in enumerate(treedata):
            parent = QTreeWidgetItem(widget)
            parent.setText(0,key)
            if isinstance(treedata[key],dict):
                includelist = includelists[i]
                walkDict(treedata[key],parent,key)
        widget.expandAll()
        widget.blockSignals(False)
        
    def handleBinNumber(self,widget,index,key,dictkey):
        if self.plotList[index]['keyID'] in self.MasterData:
            self.plotList[index]['legend'] = []
            self.nestedwidgets[dictkey]['legend'] = []
            model = self.tableList[self.plotList[index]['keyID']].model()
            x = model.getColumnData(self.plotList[index]['x axis data header'])
            cmap = plt.cm.jet
            bins = np.linspace(x.min(),x.max(),self.nestedwidgets[dictkey]['bin num'][-1].value()+1)
            y = pd.cut(x,bins)
            self.plotList[index]['x data'] = y.value_counts().sort_index()
            self.plotList[index]['color'] = cmap(np.linspace(0.,1.,self.nestedwidgets[dictkey]['bin num'][-1].value()))
            pllegends = map(str,self.plotList[index]['x data'].index.tolist())
            for container in ['megacontainer']:
                for i in reversed(range(self.nestedwidgets[dictkey][container].layout().count())): 
                    self.nestedwidgets[dictkey][container].layout().itemAt(i).widget().deleteLater()
            for i,legend in enumerate(pllegends):
                self.plotList[index]['legend'].append(legend)
                self.nestedwidgets[dictkey]['legend'].append(QLineEdit())
                self.nestedwidgets[dictkey]['legend'][-1].textChanged.connect(lambda trash, plwidget=self.nestedwidgets[dictkey]['legend'][-1],plindex=index,plkey='legend',pllistindex=i:self.EditPlotOptions(plwidget,plindex,plkey,pllistindex))
                self.nestedwidgets[dictkey]['legend'][i].setText(legend)
                j = 0
                if 'color' in self.nestedwidgets[dictkey]:
                    if i == 0:
                        self.nestedwidgets[dictkey]['megacontainer'].layout().addWidget(QLabel('Colors'),0,j,1,1)
                    self.nestedwidgets[dictkey]['megacontainer'].layout().addWidget(self.nestedwidgets[dictkey]['color'][i],i+1,j,1,1)   
                    j+=1
                if 'legend' in self.nestedwidgets[dictkey]:
                    if i == 0:
                        self.nestedwidgets[dictkey]['megacontainer'].layout().addWidget(QLabel('Legend'),0,j,1,1)
                    self.nestedwidgets[dictkey]['megacontainer'].layout().addWidget(self.nestedwidgets[dictkey]['legend'][i],i+1,j,1,1)
                    j+=1
                if 'marker' in self.nestedwidgets[dictkey]:
                    if i == 0:
                        self.nestedwidgets[dictkey]['megacontainer'].layout().addWidget(QLabel('Marker'),0,j,1,1)
                    self.nestedwidgets[dictkey]['megacontainer'].layout().addWidget(self.nestedwidgets[dictkey]['marker'][i],i+1,j,1,1)
            
        
    def handleColorbar(self,widget,index,key,dictkey):
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
                elif activated and isinstance(widgets,QLineEdit):
                    widgets.setText(self.nestedwidgets[dictkey]['colorbar'][3].currentText())
                elif not activated and isinstance(widgets,QComboBox):
                    widgets.setCurrentIndex(-1)
                elif not activated and isinstance(widgets,QLineEdit):
                    widgets.setText('')
            elif isinstance(widgets,QLabel) and widgets.text() == 'color map name:':
                colormapnameindex = i
            elif isinstance(widgets,QLabel) and widgets.text() == 'color map header:':
                colormapheaderindex = i
        if self.plotList[index]['keyID'] in self.MasterData:
            for container in ['megacontainer']:
                for i in reversed(range(self.nestedwidgets[dictkey][container].layout().count())): 
                    self.nestedwidgets[dictkey][container].layout().itemAt(i).widget().deleteLater()
            self.plotList[index]['color'] = []
            self.nestedwidgets[dictkey]['color']=[]
            self.plotList[index]['marker'] = []
            self.nestedwidgets[dictkey]['marker'] = []
            self.plotList[index]['legend'] = []
            self.nestedwidgets[dictkey]['legend'] = []
            if self.plotList[index]['plot type'] in zordertypes:
                self.nestedwidgets[dictkey]['z order'] = []
                self.plotList[index]['z order'] = []
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
                    if self.plotList[index]['plot type'] in zordertypes:
                        self.nestedwidgets[dictkey]['z order'].append(QComboBox())
                        self.nestedwidgets[dictkey]['z order'][i].addItems(map(str,np.arange(1,len(self.plotList[index]['y data'])+1,1)))
                        self.plotList[index]['z order'].append(i+1)
                        self.nestedwidgets[dictkey]['z order'][-1].currentIndexChanged.connect(lambda trash,plwidget=self.nestedwidgets[dictkey]['z order'][-1],plindex=index,plkey='z order',pllistindex=i:self.EditPlotOptions(plwidget,plindex,plkey,pllistindex))
                        nwindex = self.nestedwidgets[dictkey]['z order'][i].findText(str(i+1))
                        self.nestedwidgets[dictkey]['z order'][i].setCurrentIndex(nwindex)
                    j = 0
                    if 'color' in self.nestedwidgets[dictkey]:
                        if i == 0:
                            self.nestedwidgets[dictkey]['megacontainer'].layout().addWidget(QLabel('Colors'),0,j,1,1)
                        self.nestedwidgets[dictkey]['megacontainer'].layout().addWidget(self.nestedwidgets[dictkey]['color'][i],i+1,j,1,1)   
                        j+=1
                    if 'legend' in self.nestedwidgets[dictkey]:
                        if i == 0:
                            self.nestedwidgets[dictkey]['megacontainer'].layout().addWidget(QLabel('Legend'),0,j,1,1)
                        self.nestedwidgets[dictkey]['megacontainer'].layout().addWidget(self.nestedwidgets[dictkey]['legend'][i],i+1,j,1,1)
                        j+=1
                    if 'marker' in self.nestedwidgets[dictkey]:
                        if i == 0:
                            self.nestedwidgets[dictkey]['megacontainer'].layout().addWidget(QLabel('Marker'),0,j,1,1)
                        self.nestedwidgets[dictkey]['megacontainer'].layout().addWidget(self.nestedwidgets[dictkey]['marker'][i],i+1,j,1,1)
                        j+=1
                    if 'z order' in self.nestedwidgets[dictkey]:
                        if i == 0:
                            self.nestedwidgets[dictkey]['megacontainer'].layout().addWidget(QLabel('Z Order'),0,j,1,1)
                        self.nestedwidgets[dictkey]['megacontainer'].layout().addWidget(self.nestedwidgets[dictkey]['z order'][i],i+1,j,1,1)
                        j+=1
            else:
                nwindex = self.nestedwidgets[dictkey]['symbol code'][1].findText('False')
                self.nestedwidgets[dictkey]['symbol code'][1].setCurrentIndex(nwindex)
                self.nestedwidgets[dictkey]['symbol code'][3].setCurrentIndex(-1)
                self.nestedwidgets[dictkey]['symbol code'][3].setEnabled(False)
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
                    self.nestedwidgets[dictkey]['color'][i].setEnabled(False)
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
                    if self.plotList[index]['plot type'] in zordertypes:
                        self.nestedwidgets[dictkey]['z order'].append(QComboBox())
                        self.nestedwidgets[dictkey]['z order'][i].addItems(map(str,np.arange(1,len(self.plotList[index]['y data'])+1,1)))
                        self.plotList[index]['z order'].append(i+1)
                        self.nestedwidgets[dictkey]['z order'][-1].currentIndexChanged.connect(lambda trash,plwidget=self.nestedwidgets[dictkey]['z order'][-1],plindex=index,plkey='z order',pllistindex=i:self.EditPlotOptions(plwidget,plindex,plkey,pllistindex))
                        nwindex = self.nestedwidgets[dictkey]['z order'][i].findText(str(i+1))
                        self.nestedwidgets[dictkey]['z order'][i].setCurrentIndex(nwindex)
                    j = 0
                    if 'color' in self.nestedwidgets[dictkey]:
                        if i == 0:
                            self.nestedwidgets[dictkey]['megacontainer'].layout().addWidget(QLabel('Colors'),0,j,1,1)
                        self.nestedwidgets[dictkey]['megacontainer'].layout().addWidget(self.nestedwidgets[dictkey]['color'][i],i+1,j,1,1)   
                        j+=1
                    if 'legend' in self.nestedwidgets[dictkey]:
                        if i == 0:
                            self.nestedwidgets[dictkey]['megacontainer'].layout().addWidget(QLabel('Legend'),0,j,1,1)
                        self.nestedwidgets[dictkey]['megacontainer'].layout().addWidget(self.nestedwidgets[dictkey]['legend'][i],i+1,j,1,1)
                        j+=1
                    if 'marker' in self.nestedwidgets[dictkey]:
                        if i == 0:
                            self.nestedwidgets[dictkey]['megacontainer'].layout().addWidget(QLabel('Marker'),0,j,1,1)
                        self.nestedwidgets[dictkey]['megacontainer'].layout().addWidget(self.nestedwidgets[dictkey]['marker'][i],i+1,j,1,1)
                        j+=1
                    if 'z order' in self.nestedwidgets[dictkey]:
                        if i == 0:
                            self.nestedwidgets[dictkey]['megacontainer'].layout().addWidget(QLabel('Z Order'),0,j,1,1)
                        self.nestedwidgets[dictkey]['megacontainer'].layout().addWidget(self.nestedwidgets[dictkey]['z order'][i],i+1,j,1,1)
                        j+=1
        else:
            if activated:
                self.plotList[index]['color map'] = plt.cm.get_cmap(self.nestedwidgets[dictkey]['colorbar'][colormapnameindex+1].currentText())
                for i in range(len(self.plotList[index]['y data'])):
                    self.nestedwidgets[dictkey]['color'][i].setEnabled(False)
            else:
                self.nestedwidgets[dictkey]['colorbar'][1].setEnabled(False)
                for i in range(len(self.plotList[index]['y data'])):
                    self.nestedwidgets[dictkey]['color'][i].setEnabled(True)
                    nwindex = self.nestedwidgets[dictkey]['color'][i].findText(plotcolor[i%len(plotcolor)])
                    self.nestedwidgets[dictkey]['color'][i].setCurrentIndex(nwindex)
                self.plotList[index]['color map'] = None
        
    def handleSymbolCode(self,widget,index,key,dictkey):
        ply,plx,plz = [],[],[]
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
        if self.plotList[index]['keyID'] in self.MasterData and self.plotList[index]['unique headers']:
            origtabledata = self.tableList[self.plotList[index]['keyID']].model().getOrigData()
            origtabledata = Filter(origtabledata,self.plotList[index]['filters'])
            for container in ['megacontainer']:
                for i in reversed(range(self.nestedwidgets[dictkey][container].layout().count())): 
                    self.nestedwidgets[dictkey][container].layout().itemAt(i).widget().deleteLater()
            self.plotList[index]['color'] = []
            self.nestedwidgets[dictkey]['color']=[]
            self.plotList[index]['marker'] = []
            self.nestedwidgets[dictkey]['marker'] = []
            self.plotList[index]['legend'] = []
            self.nestedwidgets[dictkey]['legend'] = []
            if self.plotList[index]['plot type'] in zordertypes:
                self.nestedwidgets[dictkey]['z order'] = []
                self.plotList[index]['z order'] = []
            if not activated:
                self.plotList[index]['symbol code header'] = ''
                self.plotList[index]['y data'] = []
                self.plotList[index]['x data'] = []
                for i,header in enumerate(self.plotList[index]['y axis data header']):
                    self.plotList[index]['y data'].append(origtabledata[header])
                    self.plotList[index]['x data'].append(origtabledata[self.plotList[index]['x axis data header']])
                    if self.plotList[index]['plot type'] == '3D Plot':
                        self.plotList[index]['z data'].append(origtabledata[self.plotList[index]['z axis data header']])
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
                    if self.plotList[index]['plot type'] in zordertypes:
                        self.nestedwidgets[dictkey]['z order'].append(QComboBox())
                        self.nestedwidgets[dictkey]['z order'][i].addItems(map(str,np.arange(1,len(self.plotList[index]['y data'])+1,1)))
                        self.plotList[index]['z order'].append(i+1)
                        self.nestedwidgets[dictkey]['z order'][-1].currentIndexChanged.connect(lambda trash,plwidget=self.nestedwidgets[dictkey]['z order'][-1],plindex=index,plkey='z order',pllistindex=i:self.EditPlotOptions(plwidget,plindex,plkey,pllistindex))
                        nwindex = self.nestedwidgets[dictkey]['z order'][i].findText(str(i+1))
                        self.nestedwidgets[dictkey]['z order'][i].setCurrentIndex(nwindex)
                    j = 0
                    if 'color' in self.nestedwidgets[dictkey]:
                        if i == 0:
                            self.nestedwidgets[dictkey]['megacontainer'].layout().addWidget(QLabel('Colors'),0,j,1,1)
                        self.nestedwidgets[dictkey]['megacontainer'].layout().addWidget(self.nestedwidgets[dictkey]['color'][i],i+1,j,1,1)   
                        j+=1
                    if 'legend' in self.nestedwidgets[dictkey]:
                        if i == 0:
                            self.nestedwidgets[dictkey]['megacontainer'].layout().addWidget(QLabel('Legend'),0,j,1,1)
                        self.nestedwidgets[dictkey]['megacontainer'].layout().addWidget(self.nestedwidgets[dictkey]['legend'][i],i+1,j,1,1)
                        j+=1
                    if 'marker' in self.nestedwidgets[dictkey]:
                        if i == 0:
                            self.nestedwidgets[dictkey]['megacontainer'].layout().addWidget(QLabel('Marker'),0,j,1,1)
                        self.nestedwidgets[dictkey]['megacontainer'].layout().addWidget(self.nestedwidgets[dictkey]['marker'][i],i+1,j,1,1)
                        j+=1
                    if 'z order' in self.nestedwidgets[dictkey]:
                        if i == 0:
                            self.nestedwidgets[dictkey]['megacontainer'].layout().addWidget(QLabel('Z Order'),0,j,1,1)
                        self.nestedwidgets[dictkey]['megacontainer'].layout().addWidget(self.nestedwidgets[dictkey]['z order'][i],i+1,j,1,1)
                        j+=1
            else:
                nwindex = self.nestedwidgets[dictkey]['colorbar'][1].findText('False')
                self.nestedwidgets[dictkey]['colorbar'][1].setCurrentIndex(nwindex)
                self.nestedwidgets[dictkey]['colorbar'][3].setCurrentIndex(-1)
                self.nestedwidgets[dictkey]['colorbar'][3].setEnabled(False)
                self.nestedwidgets[dictkey]['colorbar'][5].setCurrentIndex(-1)
                self.nestedwidgets[dictkey]['colorbar'][5].setEnabled(False)
                self.nestedwidgets[dictkey]['colorbar'][7].setText('')
                self.nestedwidgets[dictkey]['colorbar'][7].setEnabled(False)
                self.plotList[index]['unique values'] = pd.unique(origtabledata[self.nestedwidgets[dictkey]['symbol code'][symbolcodeheaderindex+1].currentText()])
                uniquedata = origtabledata[self.nestedwidgets[dictkey]['symbol code'][symbolcodeheaderindex+1].currentText()]
                xdata = origtabledata[self.plotList[index]['x axis data header']]
                if self.plotList[index]['plot type'] == '3D Plot':
                    zdata = origtabledata[self.plotList[index]['z axis data header']]
                for i,header in enumerate(self.plotList[index]['y axis data header']):
                    if self.plotList[index]['plot type'] not in ['Timeline']:
                        ydata = origtabledata[header]
                    elif self.plotList[index]['plot type'] == 'Timeline':
                        ydata = np.array([self.plotList[index]['dset']+header]*xdata.size)
                    for j,val in enumerate(self.plotList[index]['unique values']):
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
                        self.plotList[index]['legend'].append(header+' where '+self.nestedwidgets[dictkey]['symbol code'][symbolcodeheaderindex+1].currentText()+'='+str(val))
                        self.nestedwidgets[dictkey]['legend'].append(QLineEdit())
                        self.nestedwidgets[dictkey]['legend'][-1].textChanged.connect(lambda trash, plwidget=self.nestedwidgets[dictkey]['legend'][-1],plindex=index,plkey='legend',pllistindex=(j+(i*len(self.plotList[index]['unique values']))):self.EditPlotOptions(plwidget,plindex,plkey,pllistindex))
                        self.nestedwidgets[dictkey]['legend'][-1].setText(header+' where '+self.nestedwidgets[dictkey]['symbol code'][symbolcodeheaderindex+1].currentText()+'='+str(val))
                        if self.plotList[index]['plot type'] in zordertypes:
                            self.nestedwidgets[dictkey]['z order'].append(QComboBox())
                            self.nestedwidgets[dictkey]['z order'][-1].addItems(map(str,np.arange(1,len(self.plotList[index]['y data'])+1,1)))
                            self.plotList[index]['z order'].append((j+(i*len(self.plotList[index]['unique values'])))+1)
                            self.nestedwidgets[dictkey]['z order'][-1].currentIndexChanged.connect(lambda trash,plwidget=self.nestedwidgets[dictkey]['z order'][-1],plindex=index,plkey='z order',pllistindex=(j+(i*len(self.plotList[index]['unique values']))):self.EditPlotOptions(plwidget,plindex,plkey,pllistindex))
                            nwindex = self.nestedwidgets[dictkey]['z order'][-1].findText(str((j+(i*len(self.plotList[index]['unique values'])))+1))
                            self.nestedwidgets[dictkey]['z order'][-1].setCurrentIndex(nwindex)
                        p = 0
                        if 'color' in self.nestedwidgets[dictkey]:
                            if j+(i*len(self.plotList[index]['unique values'])) == 0:
                                self.nestedwidgets[dictkey]['megacontainer'].layout().addWidget(QLabel('Colors'),0,p,1,1)
                            self.nestedwidgets[dictkey]['megacontainer'].layout().addWidget(self.nestedwidgets[dictkey]['color'][j+(i*len(self.plotList[index]['unique values']))],j+(i*len(self.plotList[index]['unique values']))+1,p,1,1)   
                            p+=1
                        if 'legend' in self.nestedwidgets[dictkey]:
                            if j+(i*len(self.plotList[index]['unique values'])) == 0:
                                self.nestedwidgets[dictkey]['megacontainer'].layout().addWidget(QLabel('Legend'),0,p,1,1)
                            self.nestedwidgets[dictkey]['megacontainer'].layout().addWidget(self.nestedwidgets[dictkey]['legend'][j+(i*len(self.plotList[index]['unique values']))],j+(i*len(self.plotList[index]['unique values']))+1,p,1,1)
                            p+=1
                        if 'marker' in self.nestedwidgets[dictkey]:
                            if j+(i*len(self.plotList[index]['unique values'])) == 0:
                                self.nestedwidgets[dictkey]['megacontainer'].layout().addWidget(QLabel('Marker'),0,p,1,1)
                            self.nestedwidgets[dictkey]['megacontainer'].layout().addWidget(self.nestedwidgets[dictkey]['marker'][j+(i*len(self.plotList[index]['unique values']))],j+(i*len(self.plotList[index]['unique values']))+1,p,1,1)
                            p+=1
                        if 'z order' in self.nestedwidgets[dictkey]:
                            if j+(i*len(self.plotList[index]['unique values'])) == 0:
                                self.nestedwidgets[dictkey]['megacontainer'].layout().addWidget(QLabel('Z Order'),0,p,1,1)
                            self.nestedwidgets[dictkey]['megacontainer'].layout().addWidget(self.nestedwidgets[dictkey]['z order'][j+(i*len(self.plotList[index]['unique values']))],j+(i*len(self.plotList[index]['unique values']))+1,p,1,1)
                            p+=1
                        idx = uniquedata == val
                        if True in idx:
                            ply.append(ydata[idx])
                            plx.append(xdata[idx])
                            if self.plotList[index]['plot type'] == '3D Plot':
                                plz.append(zdata[idx])
                self.plotList[index]['y data'] = ply
                self.plotList[index]['x data'] = plx
                if self.plotList[index]['plot type'] == '3D Plot':
                    self.plotList[index]['z data'] = plz
        else:
            pass
    def EditPlotOptions(self,widget,index,key,listindex):
        if isinstance(widget,QComboBox):
            getText = widget.currentText
        if isinstance(widget,QLineEdit):
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
        if key == 'projection':
            self.plotList[index][key] = self.tformMapper(val)
            
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
        
    def plotListPlot(self,Save=False,SaveOnly=False,Advanced=False):
        if not Advanced:
            for i in range(self.PlotTree.topLevelItemCount()):
                if self.PlotTree.topLevelItem(i).isSelected():
                    pl = self.plotList[i]
                    pltr = Plotterator.Plotter(classy=self.PlotListClassy.text(),picker=True,facecolor=pl['figure background color'])
                    if pl['plot type'] not in ['Basemap','3D Plot']:
                        pax = pltr.add_subplot()
                    elif pl['plot type'] == 'Basemap':
#                        plt.add_subplot(mapplot=True)
                        if 'Orthographic' in self.reverseTFormMapper(pl['projection']):
                            clat,clon = self.orthoCenters(pl['orthographic center'])
                            pax = pltr.add_subplot(mapplot=True,mapproj='Orthographic('+str(clon)+','+str(clat)+')')
                        else:
                            pax = pltr.add_subplot(mapplot=True,mapproj=self.reverseTFormMapper(pl['projection']))
                    elif pl['plot type'] == '3D Plot':
                        pax = pltr.add_subplot(threeD=True)
                    if pl['plot type'] in ['Scatter','Timeline']:
                        for i,ydat in enumerate(pl['y data']):
                            pltr.scatter(pl['x data'][i],ydat,c=pl['color'][i],cmap=pl['color map name'],label=pl['legend'][i],marker=pl['marker'][i],s=pl['marker size'],zorder=int(pl['z order'][i]))
                        if pl['color map']:
                            pltr.add_colorbar(pax,pl['color map name'],pl['colorbar Label'])
                    if pl['plot type'] in ['Line']:
                        for i,ydat in enumerate(pl['y data']):
                            pltr.plot(pl['x data'][i],ydat,c=pl['color'][i],label=pl['legend'][i],marker=pl['marker'][i],ms=pl['marker size']/LinePlotMarkerNormalize,ls=pl['line style'][i],lw=pl['line width']/LinePlotLineWidthNormalize,zorder=int(pl['z order'][i]))
                    if pl['plot type'] in ['Stacked']:
                        pltr.stackplot(pl['x data'][0],pl['y data'][0],colors=[colorss for colorss in pl['color']],labels=[labelss for labelss in pl['legend']])
                    if pl['plot type'] in ['Bar']:
                        ticklabels = []
                        for i,ydat in enumerate(pl['x data']):
                            if ydat.dtype.kind =='f':
                                ticklabels.append([str(round(float(val),2)) for val in ydat.value_counts().index])
                            else:
                                ticklabels.append(ydat.value_counts().index)
                            pltr.bar(pl['spacing'][i]+i*pl['bar width'],ydat.value_counts(),width=pl['bar width']*.8,color=pl['color'][i],label=pl['legend'][i],zorder=int(pl['z order'][i]))
                            pltr.parseCommand(pax,'set_xticks',[[np.concatenate([space + i*pl['bar width'] for i,space in enumerate(pl['spacing'])])]])
                            pltr.parseCommand(pax,'set_xticklabels',[[np.concatenate([tick for tick in ticklabels])]])
                    if pl['plot type'] in ['Pie']:
                        pltr.pie(pl['x data'], autopct='%.2f%%',colors=pl['color'])
                        pltr.parseCommand(pax,'set_aspect',[['equal']])
                        if not self.PlotListHideLegendChk.isChecked():
                            pltr.parseCommand('fig','legend',[dict(labels=pl['legend'],prop=dict(size=6),loc='best',ncol=4)])
                    if pl['plot type'] in ['Basemap']:
                        handles = []
                        for i,ydat in enumerate(pl['y data']):
                            if not pl['bmoa']:
                                pltr.scatter(pl['x data'][i],ydat,pax,s=pl['marker size'],c=pl['color'][i],cmap=pl['color map name'],marker=pl['marker'][i],label = pl['legend'][i],transform='PlateCarree()',zorder=int(pl['z order'][i]))
                            else:
                                for j,r in enumerate(pl['radii'][i]):
                                    if r > 0:
                                        lats,lons = ID.circleLatLons(pl['y data'][i][j],pl['x data'][i][j],r)
                                        lats,lons = ID.handle_InternationalDateline(lats,lons)
                                    else:
                                        lats,lons = ID.handle_InternationalDateline(pl['y data'][i][j],pl['x data'][i][j])
                                    for ii in range(len(lats)):
                                        pltr.add_patch(pax,'Polygon',[dict(xy=np.array([lons[ii],lats[ii]]).T,closed=True,fill=pl['fill DA'],color=pl['color'][i],alpha=pl['alpha']/100.,transform='PlateCarree()',ls=pl['DA line style'],zorder=int(pl['z order'][i]))])
                            if not self.PlotListHideLegendChk.isChecked():
                                handles.append(([0],[0],dict(color=pl['color'][i])))
                        if not self.PlotListHideLegendChk.isChecked() and pl['bmoa']:
                            #TODO make this figure legend
                            pltr.add_customlegend(pax,handles,pl['legend'],loc='best',prop=dict(size=6),ncol=4)
                        pltr.parseCommand(pax,'set_global',[])
                        if pl['color map']:
                            pltr.add_colorbar(pax,pl['color map name'],pl['colorbar Label'])
                        if self.BlueMarble.currentText() == '':
                            pass
#                            ax.add_feature(cfeature.BORDERS)
#                            ax.add_feature(cfeature.LAND)
#                            ax.add_feature(cfeature.OCEAN)
#                            ax.add_feature(cfeature.COASTLINE)
                        else:
                            pltr.add_map(self.blueMarble(self.BlueMarble.currentText()),projection='PlateCarree()')
                    if pl['plot type'] in ['3D Plot']:
                        for i in range(len(pl['y data'])):
                            pltr.scatter3d(pl['x data'][i],pl['y data'][i],pl['z data'][i],zdir='z',s=pl['marker size'],c=pl['color'][i],cmap=pl['color map name'],marker=pl['marker'][i],label=pl['legend'][i])
                        if pl['color map']:
                            pltr.add_colorbar(pax,pl['color map name'],pl['colorbar Label'])
                        pltr.parseCommand(pax,'set_zlabel',[[pl['z label']],dict(fontsize=15)])
                    if not self.PlotListHideLegendChk.isChecked() and not pl['bmoa']:
                        pltr.parseCommand('fig','legend',[dict(prop=dict(size=6),loc='best',ncol=4)])
                    pltr.parseCommand(pax,'set_xlabel',[[pl['x label']],dict(fontsize=15)])
                    pltr.parseCommand(pax,'set_ylabel',[[pl['y label']],dict(fontsize=15)])
                    pltr.parseCommand(pax,'set_title',[[pl['plot title']]])
                    pltr.parseCommand(pax,'set_facecolor',[[pl['axis background color']]])
                    if not SaveOnly:
                        pltr.createPlot('',PERSIST=True)
                    if SaveOnly:
                        filename = self.PlotListSaveDir.text().replace('*Plot-Title_TimeStamp*',pl['plot title']+str(time.strftime("%m-%d-%Y_%H_%M_%S")+'.png'))
                        print filename
                        pltr.createPlot(filename,SAVEPNG=True,SAVEPKL=True)
        if Advanced:
            self.dialog = AdvancedPlot(self.plotList,self)
            self.dialog.show()
            
            pass
    
    def updateSaveDirectory(self):
        sdir = QFileDialog.getExistingDirectory(self, "Select Directory")
        sdir = os.path.join(sdir,'*Plot-Title_TimeStamp*')
        self.PlotListSaveDir.setText(sdir)
        
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
                
    def joinStrings(self):
        if self.TableTab.count():
            self.joinstringadd = pd.DataFrame()
            index = self.TableTab.currentIndex()
            keyID = self.tableIDList[index]
            md = self.MasterData[keyID]
            model = self.tableList[keyID].model()
            headers = model.getHeaderNames()
            self.dialog = JoinString(model.getHeaderNames(),keyID,self)
            self.dialog.exec_()
            
            if self.joinstringadd.shape[0]:
                model.addColumnData(self.joinstringadd,list(self.joinstringadd))
                
    def templatePlot(self,plottype,symbolCodeHeader,colorbarHeader,xaxis,yaxis,plottedheader,symbolCode,colorbarType):
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
        for header in headers:
            if header not in self.header:
                self.header.append(header)
                self.DataOrig = self.DataOrig.join(data)
            else:
                self.DataOrig[header] = data[header]
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
    
class JoinString(QDialog):
    def __init__(self,fields,keyID,parent=None):
        super(JoinString,self).__init__(parent)
        uic.loadUi('JoinStringGui.ui', self)
        self.fields = fields
        self.keyID = keyID
        self.parent = parent
        self.makeConnections()
        self.FieldList.addItems(self.fields)
        
    def makeConnections(self):
        self.buttonBox.accepted.connect(self.Accept)
        self.buttonBox.rejected.connect(self.Reject)
        
    def Accept(self):
        selheaders = [item.text() for item in self.FieldList.selectedItems()]
        if selheaders:
            lists = []
            for header in selheaders:
                lists.append(self.parent.tableList[self.keyID].model().getColumnData(header))
            y = JoinStrings(self.HeaderName.text(),lists,self.Delimeter.text())
            self.parent.joinstringadd = y
        
    def Reject(self):
        self.close()

class SpecialTree(QTreeWidget):
    itemDropped = QtCore.pyqtSignal()
    def __init__(self,parent):
        super(SpecialTree,self).__init__(parent)
        self.parent = parent
    
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Delete:
            for i in range(self.topLevelItemCount()):
                if self.topLevelItem(i) == self.currentItem():
                    self.takeTopLevelItem(i)
        self.itemDropped.emit()
        event.accept()

class AdvancedPlotWidget(QDockWidget):

    def __init__(self,parent,plotlist,**kwargs):
        super(AdvancedPlotWidget,self).__init__(parent)
        self.Type = (None,None,None,None)
        self.parent = parent
        self.plotlist = plotlist
        self.TreeWidget = SpecialTree(self)
        self.xID = QLabel('X Axis Label:')
        self.yID = QLabel('Y Axis Label:')
        self.zID = QLabel('Z Axis Label:')
        self.AxisID = QLabel('Axis Title:')
        self.BMID = QLabel('Blue Marble:')
        self.ProjID = QLabel('Projection:')
        self.AxisColor = QPushButton('Axis Color')
        self.AxisColorVal = QLineEdit('#ffffff')
        self.AxisColorVal.setReadOnly(True)                                      
        self.XAxisLabel = QLineEdit()
        self.YAxisLabel = QLineEdit()
        self.AxisTitle = QLineEdit()
        self.ZAxisLabel = QLineEdit()
        self.BlueMarble = QComboBox()
        self.BlueMarble.addItems(BLUEMARBLE)
        self.BlueMarble.setCurrentIndex(0)
        self.GridLabel = QLabel()
        self.HideLegendChk = QCheckBox('Hide Legend')
#        self.setFloating(False)
        self.setFeatures(~QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetMovable)
        self.TypeTogether = [['Line','Scatter']]
        
        self.AxisColor.clicked.connect(lambda:self.parent.parent.colorPicker(self.AxisColorVal))
        
        Hlayout0 = QHBoxLayout()
        Hlayout0.addWidget(QLabel('Axis Gridpoint'))
        Hlayout0.addWidget(self.GridLabel)
        
        Hlayout1 = QHBoxLayout()
        Hlayout1.addWidget(self.AxisID)
        Hlayout1.addWidget(self.AxisTitle)
        
        Hlayout2 = QHBoxLayout()
        Hlayout2.addWidget(self.xID)
        Hlayout2.addWidget(self.XAxisLabel)
        
        Hlayout3 = QHBoxLayout()
        Hlayout3.addWidget(self.yID)
        Hlayout3.addWidget(self.YAxisLabel)
        
        Hlayout4 = QHBoxLayout()
        Hlayout4.addWidget(self.zID)
        Hlayout4.addWidget(self.ZAxisLabel)
        
        Hlayout5 = QHBoxLayout()
        Hlayout5.addWidget(self.BMID)
        Hlayout5.addWidget(self.BlueMarble)
        
        Hlayout6 = QHBoxLayout()
        Hlayout6.addWidget(self.AxisColor)
        Hlayout6.addWidget(self.AxisColorVal)
        
        Hlayout7 = QHBoxLayout()
        Hlayout7.addWidget(self.HideLegendChk)
        
        Vlayout = QVBoxLayout()
        Vlayout.addLayout(Hlayout0)
        Vlayout.addLayout(Hlayout1)
        Vlayout.addLayout(Hlayout2)
        Vlayout.addLayout(Hlayout3)
        Vlayout.addLayout(Hlayout4)
        Vlayout.addLayout(Hlayout5)
        Vlayout.addLayout(Hlayout6)
        Vlayout.addLayout(Hlayout7)
        Vlayout.addSpacerItem(QSpacerItem(1,1))
        self.TreeWidget.headerItem().setText(0,'Filename')
        self.TreeWidget.headerItem().setText(1,'Plot Type')
        self.TreeWidget.headerItem().setText(2,'Title')
        self.TreeWidget.headerItem().setText(3,'X Axis')
        self.TreeWidget.headerItem().setText(4,'Y Axis')
        self.TreeWidget.headerItem().setText(5,'Index')
        self.TreeWidget.setDefaultDropAction(QtCore.Qt.MoveAction)
        self.TreeWidget.setDragDropMode(QAbstractItemView.DragDrop)
        self.TreeWidget.setAcceptDrops(True)
        self.TreeWidget.setDragEnabled(True)
        self.TreeWidget.itemChanged.connect(self.setLabels)
        self.TreeWidget.itemDropped.connect(self.setLabels)
        MainLayout = QHBoxLayout()
        MainLayout.addWidget(self.TreeWidget)
        MainLayout.addLayout(Vlayout)
        widget = QWidget()
        widget.setLayout(MainLayout)
        self.setWidget(widget)
            
    def setLabels(self):
        self.TreeWidget.blockSignals(True)
        xaxislabellist = []
        yaxislabellist = []
        zaxislabellist = []
        plottitlelist = []
        index = None
        for i in range(self.TreeWidget.topLevelItemCount()):
            item = self.TreeWidget.topLevelItem(i)
            item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsDragEnabled)
            if item.text(5):
                index = int(item.text(5))
                if 'time' in self.plotlist[index]['x label'].lower():
                    xlabel = 'Time'
                else:
                    xlabel = self.plotlist[index]['x label']
                xaxislabellist.append(xlabel)
                yaxislabellist.append(self.plotlist[index]['y label'])
                plottitlelist.append(self.plotlist[index]['plot title'])
                zaxislabellist.append(self.plotlist[index]['z label'])
        if index != None:
            if self.plotlist[index]['x label']:       
                self.XAxisLabel.setText(xaxislabellist[0])
            if self.plotlist[index]['y label']:  
                self.YAxisLabel.setText('/'.join(yaxislabellist))
            if self.plotlist[index]['z label']:  
                self.ZAxisLabel.setText('/'.join(zaxislabellist))
            if self.plotlist[index]['plot title']:  
                self.AxisTitle.setText('/'.join(plottitlelist))
        else:
            self.XAxisLabel.setText('')
            self.YAxisLabel.setText('')
            self.ZAxisLabel.setText('')
            self.AxisTitle.setText('')
        self.TreeWidget.blockSignals(False)
        self.setType()
        
    def setType(self):
        if self.TreeWidget.topLevelItemCount():
            item = self.TreeWidget.topLevelItem(0)
            if item.text(5):
                index = int(item.text(5))
                xaxis = self.plotlist[index]['x axis data header']
                if 'time' in xaxis.lower():
                    xaxis = 'time'
                ptype = self.plotlist[index]['plot type']
                proj = self.plotlist[index]['projection']
                orthocent = self.plotlist[index]['orthographic center']
                for i,subtype in enumerate(self.TypeTogether):
                    if ptype in subtype:
                        subtypeindex = i
                    else: 
                        subtypeindex = -1
                if subtypeindex >= 0:
                    self.Type = (self.TypeTogether[subtypeindex],xaxis,proj,orthocent)
                else:
                    self.Type = (ptype,xaxis,proj,orthocent)
                if ptype == '3D Plot':
                    self.ZAxisLabel.show()
                    self.zID.show()
                else:
                    self.ZAxisLabel.hide()
                    self.zID.hide()
                if ptype == 'Basemap':
                    self.BlueMarble.show()
                    self.BMID.show()
                else:
                    self.BlueMarble.hide()
                    self.BMID.hide()
        else:
            self.Type = (None,None,None,None)
        
        
    
class AdvancedPlot(QDialog):
    def __init__(self,plotlist,parent=None):
        super(AdvancedPlot,self).__init__(parent)
        uic.loadUi('AdvancedPlotOptions.ui', self)
        #Actions
        SaveLayout = QAction(QIcon(), 'Save Layout', self)
        SaveLayout.triggered.connect(self.saveLayout)
        LoadLayout = QAction(QIcon(), 'Load Layout', self)
        LoadLayout.triggered.connect(self.loadLayout)
        
        self.menuBar = QMenuBar()
        self.filemenu = self.menuBar.addMenu('File')
        self.filemenu.addAction(SaveLayout)
        self.filemenu.addAction(LoadLayout)
        
        self.layout().setMenuBar(self.menuBar)
        self.plotlist = plotlist
        self.parent = parent
        self.MainSplit.setStretchFactor(1, 100)
        self.RowCombo.addItems([str(i+1) for i in range(4)])
        self.ColumnCombo.addItems([str(i+1) for i in range(4)])
        self.RowCombo.setCurrentIndex(0)
        self.ColumnCombo.setCurrentIndex(0)
        self.makeConnections()
        self.setGrid()
        
        self.PlotListData.headerItem().setText(0,'Filename')
        self.PlotListData.headerItem().setText(1,'Plot Type')
        self.PlotListData.headerItem().setText(2,'Title')
        self.PlotListData.headerItem().setText(3,'X Axis')
        self.PlotListData.headerItem().setText(4,'Y Axis')
        self.PlotListData.headerItem().setText(5,'Index')
        
        self.populateList()
    def makeConnections(self):
        self.ColumnCombo.activated.connect(lambda:self.setGrid())
        self.RowCombo.activated.connect(lambda:self.setGrid())
        self.JustDoIt.clicked.connect(lambda:self.getit(Save=False))
        self.PlotListType.activated.connect(lambda:self.populateList())
        self.PlotListData.itemSelectionChanged.connect(lambda:self.greyThings())
        self.PlotListType.activated.connect(lambda:self.greyThings(Trans=True))
        self.EnableAll.clicked.connect(lambda:self.greyThings(Trans=True))
        self.FigureColor.clicked.connect(lambda:self.parent.colorPicker(self.FigureColorValue))
        self.SaveButton.clicked.connect(lambda:self.getit(Save=True))
        
    def populateList(self):
        self.PlotListData.clear()
        for i in range(len(self.plotlist)-1):
            if self.PlotListType.currentText() == self.plotlist[i]['plot type']:
                item = QTreeWidgetItem()
                item.setText(0,self.plotlist[i]['filename'])
                item.setText(1,self.plotlist[i]['plot type'])
                item.setText(2,self.plotlist[i]['plot title'])
                item.setText(3,str(self.plotlist[i]['x axis data header']))
                item.setText(4,str(self.plotlist[i]['y axis data header']))
                item.setText(5,str(self.plotlist[i]['index']))
                self.PlotListData.addTopLevelItem(item)
        
    def setGrid(self):
        for i in reversed(range(self.LayoutGrid.count())): 
            self.LayoutGrid.itemAt(i).widget().deleteLater()
        rows = int(self.RowCombo.currentText())
        cols = int(self.ColumnCombo.currentText())
        
        #Splitter setup.. looking for something else
        self.axiswidgets = []
        self.split_V = QSplitter(Qt.Vertical)
        self.split_H = []
        for row in range(rows):
            self.axiswidgets.append([])
            self.split_H.append(QSplitter(Qt.Horizontal))
            for col in range(cols):
                w = AdvancedPlotWidget(self,self.plotlist)
                self.axiswidgets[row].append(w)
                self.split_H[-1].addWidget(self.axiswidgets[row][col])
                w.GridLabel.setText(str(row)+','+str(col))
            self.split_V.addWidget(self.split_H[-1])
        self.LayoutGrid.addWidget(self.split_V)
        
    def greyThings(self,Trans=False):
        xaxis = ''
        for i in range(self.split_V.count()):
            for j in range(self.split_H[i].count()):
                widget = self.split_H[i].widget(j)
                if not widget.visibleRegion().isEmpty():
                    if not isinstance(widget.Type[0],list):
                        if widget.Type[0] in ['Pie','Bar','Stacked'] and widget.TreeWidget.topLevelItemCount() and not Trans:
                            widget.TreeWidget.setEnabled(False)
                            continue
                    if Trans:
                        widget.TreeWidget.setEnabled(True)
                        self.PlotListData.blockSignals(True)
                        self.PlotListData.clearSelection()
                        self.PlotListData.blockSignals(False)
                    else:
                        
                        item = self.PlotListData.currentItem()
                        if item:
                            index = int(item.text(5))
                            pl = self.plotlist[index]
                            if 'time' in pl['x axis data header'].lower():
                                xaxis = 'time'
                            else:
                                xaxis = pl['x axis data header']
                            if not isinstance(widget.Type[0],list):
                                if ((pl['plot type'],xaxis,pl['projection'],pl['orthographic center']) == widget.Type) or widget.Type == (None,None,None,None):
                                    widget.TreeWidget.setEnabled(True)
                                else:
                                    widget.TreeWidget.setEnabled(False)
                            else:
                                if (pl['plot type'] in widget.Type[0] and ((xaxis,pl['projection'],pl['orthographic center']) == widget.Type[1:])) or widget.Type == (None,None,None,None):
                                    widget.TreeWidget.setEnabled(True)
                                else:
                                    widget.TreeWidget.setEnabled(False)
        
    def getit(self,Save=False):
        axdict = {}
        for i in range(self.split_V.count()):
            axdict[i]={}
            for j in range(self.split_H[i].count()):
                widget = self.split_H[i].widget(j)
                if not widget.visibleRegion().isEmpty() or j == self.split_H[i].count()-1:
                    if j != self.split_H[i].count()-1 or not widget.visibleRegion().isEmpty():
                        axdict[i][j] = []
        pltr = Plotterator.Plotter(title=self.FigureTitle.text(),classy=self.Classification.text(),picker=True,facecolor=self.FigureColorValue.text())
        for row in axdict:
            x = np.array(axdict[row].keys())
            roll = np.roll(x,-1)
            colextent = roll - x
            if len(colextent) > 1:
                colextent[-1] += self.split_H[row].count()
            if len(colextent) == 1:
                colextent[0] += self.split_H[row].count() - x[0]
            for cnum,col in enumerate(axdict[row]):
                widget = self.split_H[row].widget(col)
                axdict[row][col] = colextent[cnum]
                treewidget = widget.TreeWidget
                axistitle = widget.AxisTitle.text()
                xlabel = widget.XAxisLabel.text()
                ylabel = widget.YAxisLabel.text()
                zlabel = widget.ZAxisLabel.text()
                axiscolor = widget.AxisColorVal.text()
                if widget.Type[0] not in ['Basemap','3D Plot'] and widget.Type[0]:
                    pax = pltr.add_subplot((row,col),1,colextent[cnum])
                elif widget.Type[0] == 'Basemap':
                    if 'Orthographic' in self.parent.reverseTFormMapper(widget.Type[2]):
                        clat,clon = self.parent.orthoCenters(widget.Type[3])
                        pax = pltr.add_subplot((row,col),mapplot=True,mapproj='Orthographic('+str(clon)+','+str(clat)+')')
                    else:
                        pax = pltr.add_subplot((row,col),mapplot=True,mapproj=self.parent.reverseTFormMapper(widget.Type[2]))
                elif widget.Type[0] == '3D Plot':
                    pax = pltr.add_subplot((row,col),threeD=True)
                zorderfixer = 0
                for k in range(treewidget.topLevelItemCount()):
                    item = treewidget.topLevelItem(k)
                    index = int(item.text(5))
                    pl = self.plotlist[index]
                    if pl['plot type'] in ['Scatter','Timeline']:
                        for i,ydat in enumerate(pl['y data']):
                            pltr.scatter(pl['x data'][i],ydat,axid=pax,c=pl['color'][i],cmap=pl['color map name'],label=pl['legend'][i],marker=pl['marker'][i],s=pl['marker size'],zorder=int(pl['z order'][i])+zorderfixer)
                        if pl['color map']:
                            pltr.add_colorbar(pax,pl['color map name'],pl['colorbar Label'])
                        if not widget.HideLegendChk.isChecked():
                            pltr.parseCommand(pax,'legend',[dict(loc='best')])
                    if pl['plot type'] in ['Line']:
                        for i,ydat in enumerate(pl['y data']):
                            pltr.plot(pl['x data'][i],ydat,axid=pax,c=pl['color'][i],label=pl['legend'][i],marker=pl['marker'][i],ms=pl['marker size']/LinePlotMarkerNormalize,ls=pl['line style'][i],lw=pl['line width']/LinePlotLineWidthNormalize,zorder=int(pl['z order'][i])+zorderfixer)
                        if not widget.HideLegendChk.isChecked():
                            pltr.parseCommand(pax,'legend',[dict(loc='best')])
                    if pl['plot type'] in ['Stacked']:
                        pltr.stackplot(pl['x data'][0],pl['y data'][0],axid=pax,colors=[colorss for colorss in pl['color']],labels=[labelss for labelss in pl['legend']])
                        if not widget.HideLegendChk.isChecked():
                            pltr.parseCommand(pax,'legend',[dict(loc='best')])
                    if pl['plot type'] in ['Bar']:
                        ticklabels = []
                        for i,ydat in enumerate(pl['x data']):
                            if ydat.dtype.kind =='f':
                                ticklabels.append([str(round(float(val),2)) for val in ydat.value_counts().index])
                            else:
                                ticklabels.append(ydat.value_counts().index)
                            pltr.bar(pl['spacing'][i]+i*pl['bar width'],ydat.value_counts(),axid=pax,width=pl['bar width']*.8,color=pl['color'][i],label=pl['legend'][i],zorder=int(pl['z order'][i])+zorderfixer)
                            pltr.parseCommand(pax,'set_xticks',[[np.concatenate([space + i*pl['bar width'] for i,space in enumerate(pl['spacing'])])]])
                            pltr.parseCommand(pax,'set_xticklabels',[[np.concatenate([tick for tick in ticklabels])]])
                        if not widget.HideLegendChk.isChecked():
                            pltr.parseCommand(pax,'legend',[dict(loc='best')])
                    if pl['plot type'] in ['Pie']:
                        pltr.pie(pl['x data'],axid=pax, autopct='%.2f%%',colors=pl['color'])
                        pltr.parseCommand(pax,'set_aspect',[['equal']])
                        if not widget.HideLegendChk.isChecked():
                            pltr.parseCommand(pax,'legend',[dict(loc='best',labels=pl['legend'])])
                    if pl['plot type'] in ['Basemap']:
                        handles = []
                        for i,ydat in enumerate(pl['y data']):
                            if not pl['bmoa']:
                                pltr.scatter(pl['x data'][i],ydat,axid=pax,s=pl['marker size'],c=pl['color'][i],cmap=pl['color map name'],marker=pl['marker'][i],label = pl['legend'][i],transform='PlateCarree()',zorder=int(pl['z order'][i])+zorderfixer)
                            else:
                                for j,r in enumerate(pl['radii'][i]):
                                    if r > 0:
                                        lats,lons = ID.circleLatLons(pl['y data'][i][j],pl['x data'][i][j],r)
                                        lats,lons = ID.handle_InternationalDateline(lats,lons)
                                    else:
                                        lats,lons = ID.handle_InternationalDateline(pl['y data'][i][j],pl['x data'][i][j])
                                    for ii in range(len(lats)):
                                        pltr.add_patch(pax,'Polygon',[dict(xy=np.array([lons[ii],lats[ii]]).T,closed=True,fill=pl['fill DA'],color=pl['color'][i],alpha=pl['alpha']/100.,transform='PlateCarree()',ls=pl['DA line style'],zorder=int(pl['z order'][i])+zorderfixer)])
                                if not widget.HideLegendChk.isChecked():
                                    handles.append(([0],[0],dict(color=pl['color'][i])))
                        if not widget.HideLegendChk.isChecked() and pl['bmoa']:
                            pltr.add_customlegend(pax,handles,pl['legend'],loc='best',prop=dict(size=6),ncol=4)
                        pltr.parseCommand(pax,'set_global',[])
                        if not widget.HideLegendChk.isChecked() and not pl['bmoa']:
                            pltr.parseCommand(pax,'legend',[dict(loc='best')])
                        if pl['color map']:
                            pltr.add_colorbar(pax,pl['color map name'],pl['colorbar Label'])
                        if widget.BlueMarble.currentText() == '':
                            pass
    #                            ax.add_feature(cfeature.BORDERS)
    #                            ax.add_feature(cfeature.LAND)
    #                            ax.add_feature(cfeature.OCEAN)
    #                            ax.add_feature(cfeature.COASTLINE)
                        else:
                            pltr.add_map(self.parent.blueMarble(widget.BlueMarble.currentText()),axid=pax,projection='PlateCarree()')
                    if pl['plot type'] in ['3D Plot']:
                        for i in range(len(pl['y data'])):
                            pltr.scatter3d(pl['x data'][i],pl['y data'][i],pl['z data'][i],axid=pax,zdir='z',s=pl['marker size'],c=pl['color'][i],cmap=pl['color map name'],marker=pl['marker'][i],label=pl['legend'][i])
                        if pl['color map']:
                            pltr.add_colorbar(pax,pl['color map name'],pl['colorbar Label'])
                        if not widget.HideLegendChk.isChecked():
                            pltr.parseCommand(pax,'legend',[dict(loc='best')])
                        pltr.parseCommand(pax,'set_zlabel',[[zlabel],dict(fontsize=15)])
                    pltr.parseCommand(pax,'set_xlabel',[[xlabel],dict(fontsize=15)])
                    pltr.parseCommand(pax,'set_ylabel',[[ylabel],dict(fontsize=15)])
                    pltr.parseCommand(pax,'set_title',[[axistitle]])
                    pltr.parseCommand(pax,'set_facecolor',[[axiscolor]])
                    zorderfixer += len(pl['y data'])
        if self.GlobalLegend.isChecked():
            pltr.parseCommand('fig','legend',[dict(prop=dict(size=6),loc='best',ncol=4)])
#            pltr.createPlot('',PERSIST=True)
                
        if not Save:
            pltr.createPlot('',PERSIST=True)
        else:
            sdir = os.path.join(os.path.expanduser('~'),'Phobos_Plots')
            fname = QFileDialog.getSaveFileName(self, 'Save File',sdir,"png(*.png)")[0]
            print fname
            pltr.createPlot(fname,SAVE=True,SAVEPKL=True)
    def preview(self):
        pass
    
    def saveLayout(self):
        pickle.dump(self.split_V,open('AdvancedPlotLayout.aplyt','wb'))
        pass
    
    def loadLayout(self):
        fname = QFileDialog.getOpenFileName(self, 'Open File')
        self.LayoutGrid = pickle.load(open(fname,'rb'))
        self.getit()
       
            
        
                
    
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
#    sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),'Importerator'))
#    import Importerator
#    exports, tup = Importerator.buildDepends('Plotter\Plotter')
#    RELATIVE_LIB_PATH = Importerator.RELATIVE_LIB_PATH
#    for line in exports.splitlines():
#        try:
#            exec line in globals(), globals()
#            print(line)
#        except:
#            print('{} did not work.'.format(line))
#    
##    import FilterClass
##    import InternationalDateline as ID
##    import Plotterator as Plotterator
#    BlueMarbleHD = os.path.join(RELATIVE_LIB_PATH,'Plotter','BlueMarbleHD.png')
#    BlueMarbleSD = os.path.join(RELATIVE_LIB_PATH,'Plotter','BlueMarbleSD.jpg')
    main()