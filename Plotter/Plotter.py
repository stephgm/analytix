#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 21 16:12:00 2018

@author: Jordan
"""

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
from PyQt5 import QtSql, uic, QtOpenGL
import operator
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.qt_compat import QtCore, QtWidgets, is_pyqt5
from matplotlib.backends.backend_qt5agg import (FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure
from matplotlib import colors as mcolors
#import geopandas as gp
import cartopy
import cartopy.crs as ccrs
import time
import queue as queue
import LongFunc as lf


from mpl_toolkits.mplot3d import Axes3D


colors = dict(mcolors.BASE_COLORS, **mcolors.CSS4_COLORS)

# Sort colors by hue, saturation, value and name.
by_hsv = sorted((tuple(mcolors.rgb_to_hsv(mcolors.to_rgba(color)[:3])), name)
                for name, color in list(colors.items()))
plotcolor = [name for hsv, name in by_hsv]
operators = ['Equal To','Less Than','Greater Than','Not Equal To','In Range','Not In Range','Starts With','Does Not Start With','Ends With','Does Not End With','Contains','Does Not Contain','Ascending Order','Descending Order']
plotsymb = ['.',',','o','v','^','<','>','8','s','P','p','*','h','H','D','d']
#plotcolor = ['blue','black','red','green']
maps = sorted(m for m in plt.cm.datad if not m.endswith("_r"))
orkeys = [str(i) for i in range(10)]
orkeys.insert(0,'')


#spath = 'C:\Users\Jordan\Desktop'
spath = os.getcwd()


class Plotter(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        uic.loadUi('Plotter.ui', self)
        self.thread = []
        self.tableList = {}
        self.tableIDList = []
        self.HeaderCombo = []
        self.HeaderOperator = []
        self.UniqueValues = []
        self.FilterOr = []
        self.MasterData = {}
        self.plotList = [{}]
        self.plotColor = []
        self.plotSymbol = []
        self.makeConnections()
        self.selectDirectory()
        self.popFileName()
        self.initPlot()
        self.ColorBarNames.addItems(maps)
        self.colorbar = None
        self.NewPlot = False
        self.tableLayout = {}
        self.tableWidget = {}

        self.plotlistSymbol = []
        self.plotlistColor = []

    def makeConnections(self):
        self.FileName.activated.connect(self.popGroup)
        self.GroupName.activated.connect(self.popDset)
        self.DatasetList.currentItemChanged.connect(self.popHeaders)
        self.ClearHeaders.clicked.connect(self.HeaderList.clearSelection)
        self.ClearNative.clicked.connect(self.AddNativeHeaders.clearSelection)
        self.CreateTable.clicked.connect(self.addMasterData)
        self.TableTab.currentChanged.connect(self.addNativeHeaders)
        self.TableTab.currentChanged.connect(self.addFilterTree)
        self.AddFilter.clicked.connect(self.addFilters)
        self.FilterTree.itemChanged.connect(self.loadFilters)
        self.AddNative.clicked.connect(self.addNativeHeaderData)


        self.TableTab.currentChanged.connect(self.initPlot)
        self.PlotType.currentIndexChanged.connect(self.initPlot)
#        self.PlotType.currentIndexChanged.connect(self.initPlotOptions)
#        self.PlotType.currentIndexChanged.connect(self.setupPlotOptions)
        self.UpdatePlot.clicked.connect(self.updateCanvas)
        self.AddToPlotList.clicked.connect(self.addToPlotList)
        self.PlotListRemoveSelected.clicked.connect(self.clearPlotListSelection)
        self.ClearPlotList.clicked.connect(self.clearPlotList)
        self.PlotListPlot.clicked.connect(self.plotFigures)

        self.SymbolCode.stateChanged.connect(self.initPlot)
        self.PlotTree.itemSelectionChanged.connect(self.initPlotListOptions)
        self.UpdatePlotList.clicked.connect(self.updatePlotList)

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
                self.GroupName.addItems(list(hf.keys()))
        self.GroupName.setCurrentIndex(-1)

    def popDset(self):
        self.DatasetList.blockSignals(True)
        self.DatasetList.clear()
        self.DatasetList.blockSignals(False)
        self.HeaderList.clear()
        fpath = os.path.join(self.indir,self.FileName.currentText())
        with h5py.File(fpath,'r') as hf:
            self.DatasetList.addItems(list(hf.keys()))

    def popHeaders(self):
        self.HeaderList.clear()
        fpath = os.path.join(self.indir,self.FileName.currentText())
        dset = self.DatasetList.currentItem().text()
        with h5py.File(fpath,'r') as hf:
            self.HeaderList.addItems(list(hf[dset].dtype.fields.keys()))

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
                                   'Filters':[]}
            self.createTable()

    def addNativeHeaders(self):
        if self.TableTab.count():
            self.AddNativeHeaders.clear()
            index = self.TableTab.currentIndex()
            keyID = self.tableIDList[index]
            md = self.MasterData[keyID]
            self.AddNativeHeaders.addItems(set(md['AllH'])-set(md['SelH']))
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
                #print(hf[md['Dset']][header].dtype.kind)
                if hf[md['Dset']][header].dtype.kind == 'S':
                    data[header] = hf[md['Dset']][header][...].astype('U')
                else:
                    data[header] = hf[md['Dset']][header][...]
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
            self.tableList[key] = QTableView()
            self.tableLayout[key].addWidget(self.tableList[key])
            self.tableIDList.append(key)
            self.TableTab.addTab(self.tableWidget[key],md['Dset'])
        self.tableList[key].setModel(FieldTableModel(data,headers,self))
        self.tableList[key].selectionModel().selectionChanged.connect(self.setupPlotOptions)
        self.addNativeHeaders()
        self.initPlotOptions()
        self.TableTab.blockSignals(False)
        self.headermenu = self.tableList[key].horizontalHeader()
        self.headermenu.setContextMenuPolicy(Qt.CustomContextMenu)
        self.headermenu.customContextMenuRequested.connect(self.headerPopup)
        self.TableTab.setCurrentIndex(self.TableTab.count()-1)

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
            md['Filters'].append([md['SelH'][index],'Ascending Order','',1,''])
            self.addFilterTree()
        if action == DOAction:
            md['Filters'].append([md['SelH'][index],'Descending Order','',1,''])
            self.addFilterTree()
        if action == DeleteAction:
            self.removeHeaderData(md['SelH'][index])

    def addFilters(self):
        if self.TableTab.count():
            index = self.TableTab.currentIndex()
            keyID = self.tableIDList[index]
            md = self.MasterData[keyID]
            headers = copy.copy(md['SelH'])
            item = QTreeWidgetItem()
            item.setFlags(item.flags() | Qt.ItemIsSelectable | Qt.ItemIsUserCheckable | Qt.ItemIsEditable)
            self.HeaderCombo.append(QComboBox())
            self.HeaderOperator.append(QComboBox())
            self.FilterOr.append(QComboBox())
            self.UniqueValues.append(QComboBox())
            self.HeaderCombo[-1].addItems(headers)
            self.HeaderOperator[-1].addItems(operators)
            self.FilterOr[-1].addItems(orkeys)
            item.setText(3,'')
            item.setCheckState(0,Qt.Checked)
#            self.HeaderCombo[-1].activated.connect(self.loadFilters)
            self.HeaderCombo[-1].activated.connect(self.uniqueValues)
            self.HeaderOperator[-1].activated.connect(self.loadFilters)
            self.FilterOr[-1].activated.connect(self.loadFilters)
            self.UniqueValues[-1].activated.connect(self.loadFilters)
            self.HeaderCombo[-1].setCurrentIndex(0)
            self.HeaderOperator[-1].setCurrentIndex(0)
            self.FilterOr[-1].setCurrentIndex(-1)
            self.FilterTree.addTopLevelItem(item)
            if self.tableList[keyID].model().getDtype(headers[0]) == 'O':
                vals = self.tableList[keyID].model().getColumnData(headers[0])
                self.UniqueValues[-1].addItems(pd.unique(vals))
                self.FilterTree.setItemWidget(item,3,self.UniqueValues[-1])
            self.FilterTree.setItemWidget(item,1,self.HeaderCombo[-1])
            self.FilterTree.setItemWidget(item,2,self.HeaderOperator[-1])
            self.FilterTree.setItemWidget(item,4,self.FilterOr[-1])
            md['Filters'].append([self.HeaderCombo[-1].currentText(),self.HeaderOperator[-1].currentText(),item.text(3),0,self.FilterOr[-1].currentText()])

    def loadFilters(self):
        if self.TableTab.count():
            procedures = []
            index = self.TableTab.currentIndex()
            keyID = self.tableIDList[index]
            md = self.MasterData[keyID]
            headers = copy.copy(md['SelH'])

            for i in range(self.FilterTree.topLevelItemCount()):
                item = self.FilterTree.topLevelItem(i)
                md['Filters'][i][0] = self.HeaderCombo[i].currentText()
                md['Filters'][i][1] = self.HeaderOperator[i].currentText()
                if self.tableList[keyID].model().getDtype(self.HeaderCombo[i].currentText()) == 'O':
                    md['Filters'][i][2] = self.UniqueValues[-1].currentText()
                else:
                    md['Filters'][i][2] = item.text(3)
                md['Filters'][i][4] = self.FilterOr[i].currentText()
                if item.checkState(0) == Qt.Checked:
                    md['Filters'][i][3] = 1
                    procedures.append([md['Filters'][i][0],md['Filters'][i][1],md['Filters'][i][2],md['Filters'][i][4]])
                else:
                    md['Filters'][i][3] = 0
            self.tableList[keyID].model().filterTable(procedures)
            self.updateCanvas()

    def addFilterTree(self):
        if self.TableTab.count():
            self.FilterTree.clear()
            self.HeaderCombo = []
            self.HeaderOperator = []
            self.FilterOr = []
            index = self.TableTab.currentIndex()
            keyID = self.tableIDList[index]
            md = self.MasterData[keyID]
            filts = md['Filters']
            headers = copy.copy(md['SelH'])
            for filt in filts:
                if filt[0] not in headers:
                    continue
                item = QTreeWidgetItem()
                item.setFlags(item.flags() | Qt.ItemIsSelectable | Qt.ItemIsUserCheckable | Qt.ItemIsEditable)
                self.HeaderCombo.append(QComboBox())
                self.HeaderOperator.append(QComboBox())
                self.FilterOr.append(QComboBox())
                self.UniqueValues.append(QComboBox())
                self.HeaderCombo[-1].addItems(headers)
                self.HeaderOperator[-1].addItems(operators)
                self.FilterOr[-1].addItems(orkeys)
                item.setText(3,filt[2])
                if filt[3] == 1:
                    item.setCheckState(0,Qt.Checked)
                else:
                    item.setCheckState(0,Qt.Unchecked)
#                self.HeaderCombo[-1].activated.connect(self.loadFilters)
                self.HeaderCombo[-1].activated.connect(self.uniqueValues)
                self.HeaderOperator[-1].activated.connect(self.loadFilters)
                self.FilterOr[-1].activated.connect(self.loadFilters)
                self.UniqueValues[-1].activated.connect(self.loadFilters)
                index = self.HeaderCombo[-1].findText(filt[0])
                self.HeaderCombo[-1].setCurrentIndex(index)
                index = self.HeaderOperator[-1].findText(filt[1])
                self.HeaderOperator[-1].setCurrentIndex(index)
                index = self.FilterOr[-1].findText(filt[4])
                self.FilterOr[-1].setCurrentIndex(index)
                if self.tableList[keyID].model().getDtype(headers[0]) == 'O':
                    vals = self.tableList[keyID].model().getColumnData(headers[0])
                    self.UniqueValues[-1].addItems(pd.unique(vals))
                    index = self.UniqueValues[-1].findText(filt[4])
                    self.UniqueValues[-1].setCurrentIndex(index)
                    self.FilterTree.setItemWidget(item,3,self.UniqueValues[-1])
                self.FilterTree.addTopLevelItem(item)
                self.FilterTree.setItemWidget(item,1,self.HeaderCombo[-1])
                self.FilterTree.setItemWidget(item,2,self.HeaderOperator[-1])
                self.FilterTree.setItemWidget(item,4,self.FilterOr[-1])
            self.loadFilters()

    def uniqueValues(self):
        if self.TableTab.count():
            index = self.TableTab.currentIndex()
            keyID = self.tableIDList[index]
            md = self.MasterData[keyID]
            for i in range(self.FilterTree.topLevelItemCount()):
                item = self.FilterTree.topLevelItem(i)
                if self.tableList[keyID].model().getDtype(self.HeaderCombo[i].currentText()) == 'O':
                    vals = self.tableList[keyID].model().getColumnData(self.HeaderCombo[i].currentText())
                    self.UniqueValues[i] = QComboBox()
                    self.UniqueValues[i].addItems(pd.unique(vals))
                    self.FilterTree.setItemWidget(item,3,self.UniqueValues[i])
                    item.setText(3,'')
                else:
                    try:
                        txt = item.text(3)
                    except:
                        txt = ''
                    self.UniqueValues[i].clear()
                    self.FilterTree.removeItemWidget(item,3)
                    item.setText(3,txt)
            self.loadFilters()

    def initPlot(self,initPlotOption=True):
        types = self.PlotType.currentText()
        for i in reversed(list(range(self.PlotLayout.count()))):
            widgetToRemove = self.PlotLayout.itemAt(i).widget()
            self.PlotLayout.removeWidget(widgetToRemove)
            widgetToRemove.deleteLater()
        if types not in ['Basemap','3D Plot']:
            self.dynamic_canvas = FigureCanvas(Figure())
            plotCanvasLabel = QLabel()
            plotCanvasLabel.setText('Preview of Plot.  Figure can be saved using toolbar.')
            plotCanvasLabel.setAlignment(Qt.AlignCenter)
            self.PlotLayout.addWidget(NavigationToolbar(self.dynamic_canvas,self))
            self.PlotLayout.addWidget(plotCanvasLabel)
            self.PlotLayout.addWidget(self.dynamic_canvas)
            self._dynamic_ax = self.dynamic_canvas.figure.subplots()
            self._dynamic_ax.figure.tight_layout()
            self._dynamic_ax.set_aspect('auto')
        elif types == 'Basemap':
            self.dynamic_canvas = FigureCanvas(Figure())
            plotCanvasLabel = QLabel()
            plotCanvasLabel.setText('Preview of Plot.  Figure can be saved using toolbar.')
            plotCanvasLabel.setAlignment(Qt.AlignCenter)
            self.PlotLayout.addWidget(NavigationToolbar(self.dynamic_canvas,self))
            self.PlotLayout.addWidget(plotCanvasLabel)
            self.PlotLayout.addWidget(self.dynamic_canvas)
#            if self.PlotColorBar.currentText() == 'PlateCarree':
            self._dynamic_ax = self.dynamic_canvas.figure.subplots(subplot_kw={'projection':ccrs.PlateCarree()})
#            if self.PlotColorBar.currentText() == 'Polar':
#                self._dynamic_ax = self.dynamic_canvas.figure.subplots(subplot_kw={'projection':ccrs.NorthPolarStereo()})
#            if self.PlotColorBar.currentText() == 'Orange Peel':
#                self._dynamic_ax = self.dynamic_canvas.figure.subplots(subplot_kw={'projection':ccrs.InterruptedGoodeHomolosine()})
            self._dynamic_ax.figure.tight_layout()
            self._dynamic_ax.set_aspect('auto')
        elif types == '3D Plot':
            self.dynamic_canvas = FigureCanvas(Figure())
            plotCanvasLabel = QLabel()
            plotCanvasLabel.setText('Preview of Plot.  Figure can be saved using toolbar.')
            plotCanvasLabel.setAlignment(Qt.AlignCenter)
            self.PlotLayout.addWidget(plotCanvasLabel)
            self.PlotLayout.addWidget(NavigationToolbar(self.dynamic_canvas,self))
            self.PlotLayout.addWidget(self.dynamic_canvas)
            self._dynamic_ax = Axes3D(self.dynamic_canvas.figure)
            self._dynamic_ax.figure.tight_layout()
            self._dynamic_ax.set_aspect('auto')
        if initPlotOption:
            self.initPlotOptions()

    def initPlotOptions(self):
        if self.TableTab.count():
            self.PlotColorSymbol.clear()
            self.NewPlot = False
            self.PlotXAxis.clear()
            self.PlotColorBar.clear()
            index = self.TableTab.currentIndex()
            keyID = self.tableIDList[index]
            md = self.MasterData[keyID]
            headers = self.tableList[keyID].model().getHeaderNames()
            nsheaders = []
            for header in headers:
                if self.tableList[keyID].model().getDtype(header) != 'O':
                    nsheaders.append(header)
            self.PlotXAxis.addItems(headers)
            self.PlotXAxis.setCurrentIndex(-1)
            self.PlotColorBar.addItem('')
            self.PlotColorBar.addItems(nsheaders)
            self.tableList[keyID].selectionModel().clearSelection()

            if self.PlotType.currentText() == 'Scatter':
                self.MarkerSizeLabel.setText('Marker Size:')
                self.FontSizeLabel.setText('Font Size:')
                self.LineWidthLabel.setText('Line Width:')
                self.ColorBarLabelID.setText('Color Bar On Header')
                self.PlotColorBar.setEnabled(True)
                self.ColorBarNames.setEnabled(True)
                self.ColorBarLabel.setEnabled(True)
                self.PlotMarkerSize.setEnabled(True)
                self.PlotLineWidth.setEnabled(True)
                self.PlotFontSize.setEnabled(True)
                self.PlotXAxis.setEnabled(True)
                self.YAxisLabel.setEnabled(True)
                self.PlotColorSymbol.setEnabled(True)
                self.SymbolCode.setEnabled(True)
                self.ZAxisLabel.setEnabled(False)
                if self.SymbolCode.isChecked():
                    self.PlotColorBar.setEnabled(False)
                    self.ColorBarNames.setEnabled(False)
                    self.ColorBarLabel.setEnabled(False)

            if self.PlotType.currentText() == 'Pie':
                self.FontSizeLabel.setText('Bin Number:')
                self.MarkerSizeLabel.setText('Marker Size:')
                self.LineWidthLabel.setText('Line Width:')
                self.ColorBarLabelID.setText('Color Bar On Header')
                self.PlotColorBar.setEnabled(False)
                self.ColorBarNames.setEnabled(False)
                self.ColorBarLabel.setEnabled(False)
                self.PlotMarkerSize.setEnabled(False)
                self.PlotLineWidth.setEnabled(False)
                self.PlotFontSize.setEnabled(True)
                self.PlotXAxis.setEnabled(True)
                self.YAxisLabel.setEnabled(False)
                self.PlotColorSymbol.setEnabled(False)
                self.SymbolCode.setEnabled(False)
                self.SymbolCode.setChecked(False)
                self.ZAxisLabel.setEnabled(False)

            if self.PlotType.currentText() == 'Bar':
                self.FontSizeLabel.setText('Bin Number:')
                self.MarkerSizeLabel.setText('Bar Width:')
                self.LineWidthLabel.setText('Bar Spacing:')
                self.ColorBarLabelID.setText('Color Bar On Header')
                self.PlotColorBar.setEnabled(False)
                self.ColorBarNames.setEnabled(False)
                self.ColorBarLabel.setEnabled(False)
                self.PlotMarkerSize.setEnabled(True)
                self.PlotLineWidth.setEnabled(True)
                self.PlotFontSize.setEnabled(True)
                self.PlotXAxis.setEnabled(True)
                self.YAxisLabel.setEnabled(True)
                self.PlotColorSymbol.setEnabled(True)
                self.SymbolCode.setEnabled(False)
                self.SymbolCode.setChecked(False)
                self.ZAxisLabel.setEnabled(False)

            if self.PlotType.currentText() == 'Basemap':
                self.ColorBarLabelID.setText('Color Bar On Header')
                self.MarkerSizeLabel.setText('Marker Size:')
                self.FontSizeLabel.setText('Font Size:')
                self.LineWidthLabel.setText('Line Width:')
                self.PlotColorBar.setEnabled(True)
                self.ColorBarNames.setEnabled(True)
                self.ColorBarLabel.setEnabled(True)
                self.PlotMarkerSize.setEnabled(True)
                self.PlotLineWidth.setEnabled(True)
                self.PlotFontSize.setEnabled(True)
                self.PlotXAxis.setEnabled(False)
                self.YAxisLabel.setEnabled(True)
                self.PlotColorSymbol.setEnabled(True)
                self.PlotXAxis.setCurrentIndex(0)
                self.SymbolCode.setEnabled(False)
                self.SymbolCode.setChecked(False)
                self.ZAxisLabel.setEnabled(False)

            if self.PlotType.currentText() == '3D Plot':
                self.MarkerSizeLabel.setText('Marker Size:')
                self.FontSizeLabel.setText('Font Size:')
                self.LineWidthLabel.setText('Line Width:')
                self.ColorBarLabelID.setText('Color Bar On Header')
                self.PlotColorBar.setEnabled(True)
                self.ColorBarNames.setEnabled(True)
                self.ColorBarLabel.setEnabled(True)
                self.PlotMarkerSize.setEnabled(True)
                self.PlotLineWidth.setEnabled(True)
                self.PlotFontSize.setEnabled(True)
                self.PlotXAxis.setEnabled(False)
                self.YAxisLabel.setEnabled(True)
                self.PlotColorSymbol.setEnabled(True)
                self.PlotXAxis.setCurrentIndex(0)
                self.SymbolCode.setEnabled(False)
                self.ZAxisLabel.setEnabled(True)
            self.setupPlotOptions()

    def setupPlotOptions(self):
        index = self.TableTab.currentIndex()
        keyID = self.tableIDList[index]
        md = self.MasterData[keyID]
        self.PlotColorSymbol.clear()
        self.plotColor = []
        self.plotSymbol = []
        if self.tableList[keyID].selectionModel().selectedColumns():
            if self.PlotType.currentText() not in ['BaseMap','3D Plot']:
                headers = self.tableList[keyID].model().getHeaderNames()
                for i,index in enumerate(self.tableList[keyID].selectionModel().selectedColumns()):
                    if not self.SymbolCode.isChecked():
                        item = QTreeWidgetItem()
                        self.plotSymbol.append(QComboBox())
                        self.plotColor.append(QComboBox())
                        self.plotSymbol[-1].addItems(plotsymb)
                        self.plotColor[-1].addItems(plotcolor)
                        item.setText(0,headers[index.column()])
                        item.setText(1,'All')
                        item.setText(4,headers[index.column()])
                        item.setFlags(item.flags() | Qt.ItemIsSelectable | Qt.ItemIsEditable)
                        self.plotColor[-1].activated.connect(self.updateCanvas)
                        self.plotSymbol[-1].activated.connect(self.updateCanvas)
                        self.PlotColorSymbol.addTopLevelItem(item)
                        self.PlotColorSymbol.setItemWidget(item,2,self.plotColor[-1])
                        self.PlotColorSymbol.setItemWidget(item,3,self.plotSymbol[-1])
                        self.plotColor[-1].setCurrentIndex(i%len(plotcolor))
                        self.plotSymbol[-1].setCurrentIndex(i%len(plotsymb))
                    else:
                        uniquevals = pd.unique(self.tableList[keyID].model().getColumnData(headers[index.column()]))
                        if len(uniquevals) > 50:
                            self.SymbolCode.blockSignals(True)
                            self.SymbolCode.setChecked(False)
                            self.SymbolCode.blockSignals(False)
                            self.PlotColorBar.setEnabled(True)
                            self.ColorBarNames.setEnabled(True)
                            self.ColorBarLabel.setEnabled(True)
                            self.setupPlotOptions()
                            return
                        for j,val in enumerate(uniquevals):
                            item = QTreeWidgetItem()
                            self.plotSymbol.append(QComboBox())
                            self.plotColor.append(QComboBox())
                            self.plotSymbol[-1].addItems(plotsymb)
                            self.plotColor[-1].addItems(plotcolor)
                            item.setText(0,headers[index.column()])
                            item.setText(1,str(val))
                            item.setText(4,headers[index.column()]+':'+str(val))
                            item.setFlags(item.flags() | Qt.ItemIsSelectable | Qt.ItemIsEditable)
                            self.plotColor[-1].activated.connect(self.updateCanvas)
                            self.plotSymbol[-1].activated.connect(self.updateCanvas)
                            self.PlotColorSymbol.addTopLevelItem(item)
                            self.PlotColorSymbol.setItemWidget(item,2,self.plotColor[-1])
                            self.PlotColorSymbol.setItemWidget(item,3,self.plotSymbol[-1])
                            self.plotColor[-1].setCurrentIndex(j%len(plotcolor))
                            self.plotSymbol[-1].setCurrentIndex(j%len(plotsymb))
            self.updateCanvas()

        if self.PlotType.currentText() in ['Basemap','3D Plot']:
            item = QTreeWidgetItem()
            self.plotSymbol.append(QComboBox())
            self.plotColor.append(QComboBox())
            self.plotSymbol[-1].addItems(plotsymb)
            self.plotColor[-1].addItems(plotcolor)
            item.setText(0,'Coordinates')
            item.setText(1,'All')
            item.setText(4,'N/A for this type')
            item.setFlags(item.flags() | Qt.ItemIsSelectable | Qt.ItemIsEditable)
            self.plotColor[-1].activated.connect(self.updateCanvas)
            self.plotSymbol[-1].activated.connect(self.updateCanvas)
            self.PlotColorSymbol.addTopLevelItem(item)
            self.PlotColorSymbol.setItemWidget(item,2,self.plotColor[-1])
            self.PlotColorSymbol.setItemWidget(item,3,self.plotSymbol[-1])
            self.updateCanvas()

    def updateCanvas(self):

        #If table is removed need to get the headers from the table so that colorbar can be changed.
        #Or just remove colorbar changing setting in plotlistoptions
        self._dynamic_ax.clear()
        self._dynamic_ax.set_aspect('auto')
        if self.TableTab.count() and self.PlotXAxis.currentText():
            index = self.TableTab.currentIndex()
            keyID = self.tableIDList[index]
            headers = self.tableList[keyID].model().getHeaderNames()
            y = []
            x = []
            ylabel = ''
            colorbarlabel = ''
            marker = []
            color = []
            label = []
            plottedheader = []
            md = self.MasterData[keyID]
            pl = self.plotList
            if self.colorbar:
                try:
                    self.colorbar.remove()
                except:
                    print('hope this works')
            if self.PlotTitle.text():
                title = self.PlotTitle.text()
            else:
                title = ''
            if self.XAxisLabel.text():
                xlabel = self.XAxisLabel.text()
            else:
                xlabel = self.PlotXAxis.currentText()

            if self.PlotType.currentText() == 'Scatter' and self.tableList[keyID].selectionModel().selectedColumns():
                for index in self.tableList[keyID].selectionModel().selectedColumns():
                    if not self.SymbolCode.isChecked():
                        y.append(self.tableList[keyID].model().getColumnData(headers[index.column()]))
                        x.append(self.tableList[keyID].model().getColumnData(self.PlotXAxis.currentText()))
                    else:
                        ydata = self.tableList[keyID].model().getColumnData(headers[index.column()])
                        uniquevals = pd.unique(self.tableList[keyID].model().getColumnData(headers[index.column()]))
                        xdata = self.tableList[keyID].model().getColumnData(self.PlotXAxis.currentText())
                        for i,val in enumerate(uniquevals):
                            idx = ydata==val
                            y.append(ydata[idx])
                            x.append(xdata[idx])
                    plottedheader.append(headers[index.column()])
                    if self.YAxisLabel.text():
                        ylabel = self.YAxisLabel.text()
                    else:
                        if ylabel == '':
                            ylabel = headers[index.column()]
                        else:
                            ylabel = ylabel + ' / ' + headers[index.column()]
                markersize = self.PlotMarkerSize.value()
                linewidth = self.PlotLineWidth.value()
                for i,ydat in enumerate(y):
                    item = self.PlotColorSymbol.topLevelItem(i)
                    marker.append(self.plotSymbol[i].currentText())
                    label.append(item.text(4))
                    if self.PlotColorBar.currentText():
                        color.append(self.tableList[keyID].model().getColumnData(self.PlotColorBar.currentText()))
                        cm = plt.cm.get_cmap(self.ColorBarNames.currentText())
                    else:
                        color.append(self.plotColor[i].currentText())
                        cm = None
                    if not self.SymbolCode.isChecked():
                        sc = self._dynamic_ax.scatter(x[0], ydat, s = markersize,
                                                 c = color[i], cmap = cm, marker = marker[i], label = label[i])
                    else:
                        sc = self._dynamic_ax.scatter(x[i], ydat, s = markersize,
                                                 c = color[i], cmap = cm, marker = marker[i], label = label[i])
                if self.PlotColorBar.currentText():
                    self.colorbar = self._dynamic_ax.figure.colorbar(sc)
                    if self.ColorBarLabel.text():
                        colorbarlabel = self.ColorBarLabel.text()
                    else:
                        colorbarlabel = self.PlotColorBar.currentText()
                    self.colorbar.set_label(colorbarlabel)
                self._dynamic_ax.legend().draggable()
                self.plotList[-1] = {'xlabel':xlabel,
                                     'ylabel':ylabel,
                                     'plotTitle':title,
                                     'xdata':x,
                                     'ydata':y,
                                     'xAxisDataHeader':self.PlotXAxis.currentText(),
                                     'yAxisDataHeader':plottedheader,
                                     'symbolCode':self.SymbolCode.isChecked(),
                                     'color':color,
                                     'colorMap':cm,
                                     'colorMapHeader':self.PlotColorBar.currentText(),
                                     'colorMapName':self.ColorBarNames.currentText(),
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



            if self.PlotType.currentText() == 'Pie':
                self._dynamic_ax.set_aspect(1)
                binnum = int(self.PlotFontSize.value())
                x = self.tableList[keyID].model().getColumnData(self.PlotXAxis.currentText())
                if len(pd.unique(x)) > 20 and x.dtype.kind != 'O':
                    bins = np.linspace(x.min(),x.max(),binnum+1)
                    y = pd.cut(x,bins)
                    counts = y.value_counts().sort_index()
                    cmap = plt.cm.jet
                    colors = cmap(np.linspace(0., 1., binnum))
                else:
                    u = len(pd.unique(x))
                    cmap = plt.cm.jet
                    colors = cmap(np.linspace(0.,1.,u))
                    counts = x.value_counts().sort_index()
                sc = self._dynamic_ax.pie(counts,autopct = '%.2f%%',colors=colors)
                self._dynamic_ax.legend(counts.index).draggable()
                self.plotList[-1] = {'plotTitle':title,
                                     'xdata':counts,
                                     'xlabel':xlabel,
                                     'ylabel':'N/A',
                                     'binNum':binnum,
                                     'xAxisDataHeader':self.PlotXAxis.currentText(),
                                     'color':colors,
                                     'legend':counts.index,
                                     'keyID':keyID,
                                     'path':md['Path'],
                                     'filename':md['Filename'],
                                     'group':md['Grp'],
                                     'dset':md['Dset'],
                                     'plotType':self.PlotType.currentText()}



            if self.PlotType.currentText() == 'Bar':
                if self.YAxisLabel.text():
                    ylabel = self.YAxisLabel.text()
                else:
                    ylabel = 'Number of Occurences'
                markersize = self.PlotMarkerSize.value()
                linewidth = self.PlotLineWidth.value()
                x = self.tableList[keyID].model().getColumnData(self.PlotXAxis.currentText())
                self._dynamic_ax.set_aspect('auto')
                if len(pd.unique(x)) > 100:
                    print('too many values')
                    return
                spacing = [i*(linewidth) for i in range(len(pd.unique(x)))]
                sc = self._dynamic_ax.bar(spacing,x.value_counts(),markersize,tick_label=x.value_counts().index)
                self.plotList[-1] = {'spacing':spacing,
                                     'barspace':linewidth,
                                     'barwidth':markersize,
                                     'xlabel':xlabel,
                                     'ylabel':ylabel,
                                     'plotTitle':title,
                                     'xdata':x.value_counts(),
                                     'xAxisDataHeader':self.PlotXAxis.currentText(),
                                     'color':color,
                                     'legend':x.value_counts().index,
                                     'keyID':keyID,
                                     'path':md['Path'],
                                     'filename':md['Filename'],
                                     'group':md['Grp'],
                                     'dset':md['Dset'],
                                     'plotType':self.PlotType.currentText()}



            if self.PlotType.currentText() == 'Basemap':
                lat = self.tableList[keyID].model().getColumnData('timeTankTrack')
                lon = self.tableList[keyID].model().getColumnData('timeRvTrack')
                marker = self.plotSymbol[0].currentText()
                markersize = self.PlotMarkerSize.value()
                linewidth = self.PlotLineWidth.value()
                if self.PlotColorBar.currentText():
                    color = self.tableList[keyID].model().getColumnData(self.PlotColorBar.currentText())
                    print(color)
                    cm = plt.cm.get_cmap(self.ColorBarNames.currentText())
                else:
                    color = self.plotColor[0].currentText()
                    cm = None
#                if self.PlotColorBar.currentText() == 'PlateCarree':
                tform = ccrs.PlateCarree()
#                if self.PlotColorBar.currentText() == 'Polar':
#                    tform = ccrs.NorthPolarStereo()
#                if self.PlotColorBar.currentText() == 'Orange Peel':
#                    tform = ccrs.InterruptedGoodeHomolosine()
#                self._dynamic_ax.stock_img()
                self._dynamic_ax.add_feature(cartopy.feature.COASTLINE)
                self._dynamic_ax.add_feature(cartopy.feature.BORDERS)
                self._dynamic_ax.add_feature(cartopy.feature.LAND)
                self._dynamic_ax.add_feature(cartopy.feature.OCEAN)

                sc = self._dynamic_ax.scatter(lon, lat, s = markersize,
                                     c = color, cmap = cm, marker = marker, transform=tform)
                if self.PlotColorBar.currentText():
                    self.colorbar = self._dynamic_ax.figure.colorbar(sc)
                    if self.ColorBarLabel.text():
                        colorbarlabel = self.ColorBarLabel.text()
                    else:
                        colorbarlabel = self.PlotColorBar.currentText()
                    self.colorbar.set_label(colorbarlabel)
                self._dynamic_ax.set_adjustable('datalim')
                self.plotList[-1] = {'plotTitle':title,
                                     'xdata':lon,
                                     'ydata':lat,
                                     'xlabel':'lon',
                                     'ylabel':'lat',
                                     'xAxisDataHeader':'lon',
                                     'color':color,
                                     'colorMap':cm,
                                     'colorMapHeader':self.PlotColorBar.currentText(),
                                     'colorMapName':self.ColorBarNames.currentText(),
                                     'marker':marker,
                                     'markersize':markersize,
                                     'colorbarLabel':colorbarlabel,
                                     'projection':tform,
                                     'keyID':keyID,
                                     'path':md['Path'],
                                     'filename':md['Filename'],
                                     'group':md['Grp'],
                                     'dset':md['Dset'],
                                     'plotType':self.PlotType.currentText()}



            if self.PlotType.currentText() == '3D Plot':
                x = self.tableList[keyID].model().getColumnData('timeTankTrack')
                y = self.tableList[keyID].model().getColumnData('timeRvTrack')
                z = self.tableList[keyID].model().getColumnData('timeRvTrack')
                if self.YAxisLabel.text():
                    ylabel = self.YAxisLabel.text()
                else:
                    ylabel = 'timeRvTrack'
                if self.ZAxisLabel.text():
                    zlabel = self.ZAxisLabel.text()
                else:
                    zlabel = 'timeRvTrack'
                marker = self.plotSymbol[0].currentText()
                markersize = self.PlotMarkerSize.value()
                linewidth = self.PlotLineWidth.value()
                if self.PlotColorBar.currentText():
                        color = self.tableList[keyID].model().getColumnData(self.PlotColorBar.currentText())
                        cm = plt.cm.get_cmap(self.ColorBarNames.currentText())
                else:
                    color = self.plotColor[0].currentText()
                    cm = None
                sc = self._dynamic_ax.scatter(x, y, z, zdir = 'z', s = markersize,
                                                 c = color, cmap = cm, marker = marker)
                if self.PlotColorBar.currentText():
                    self.colorbar = self._dynamic_ax.figure.colorbar(sc)
                    if self.ColorBarLabel.text():
                        colorbarlabel = self.ColorBarLabel.text()
                    else:
                        colorbarlabel = self.PlotColorBar.currentText()
                    self.colorbar.set_label(colorbarlabel)
                self._dynamic_ax.set_zlabel(zlabel)
                self.plotList[-1] = {'xlabel':xlabel,
                                     'ylabel':ylabel,
                                     'zlabel':zlabel,
                                     'plotTitle':title,
                                     'xdata':x,
                                     'ydata':y,
                                     'zdata':z,
                                     'xAxisDataHeader':'XPos',
                                     'color':color,
                                     'colorMap':cm,
                                     'colorMapHeader':self.PlotColorBar.currentText(),
                                     'colorMapName':self.ColorBarNames.currentText(),
                                     'marker':marker,
                                     'markersize':markersize,
                                     'colorbarLabel':colorbarlabel,
                                     'keyID':keyID,
                                     'path':md['Path'],
                                     'filename':md['Filename'],
                                     'group':md['Grp'],
                                     'dset':md['Dset'],
                                     'plotType':self.PlotType.currentText()}

            self._dynamic_ax.set_title(title)
            self._dynamic_ax.set_xlabel(xlabel)
            self._dynamic_ax.set_ylabel(ylabel)
            self._dynamic_ax.figure.tight_layout()
            self._dynamic_ax.figure.canvas.draw()
            self.NewPlot = True

    def addToPlotList(self):
        if self.NewPlot:
            index = self.TableTab.currentIndex()
            keyID = self.tableIDList[index]
            md = self.MasterData[keyID]
            pl = self.plotList[-1]
            item = QTreeWidgetItem()
            item.setText(0,md['Filename'])
            item.setText(1,pl['plotType'])
            item.setText(2,pl['plotTitle'])
            item.setText(3,pl['xlabel'])
            item.setText(4,pl['ylabel'])
            item.setText(5,str(len(self.plotList)))
            item.setText(6,pl['xAxisDataHeader'])
            self.PlotTree.addTopLevelItem(item)
            self.plotList.append({})
            self.initPlot(False)
            return

    def clearPlotListSelection(self):
#        if self.PlotTree.currentIndex():
        for i in range(self.PlotTree.topLevelItemCount()-1,-1,-1):
            if self.PlotTree.topLevelItem(i).isSelected():
                item = self.PlotTree.topLevelItem(i)
                index = item.text(5)
                self.plotList.pop(i)
                self.PlotTree.takeTopLevelItem(i)
        return

    def clearPlotList(self):
        self.PlotTree.clear()
        self.plotList = [{}]

    def initPlotListOptions(self):
        self.PlotListTitle.setEnabled(True)
        self.PlotListXAxisLabel.setEnabled(True)
        self.PlotListYAxisLabel.setEnabled(True)
        self.PlotListZAxisLabel.setEnabled(True)
        self.PlotListBin.setEnabled(True)
        self.PlotListBarWidth.setEnabled(True)
        self.PlotListBarSpacing.setEnabled(True)
        self.PlotListColorBarHeader.setEnabled(True)
        self.PlotListColorBarName.setEnabled(True)
        self.PlotListColorBarLabel.setEnabled(True)
        self.PlotListFontSize.setEnabled(True)
        self.PlotListMarkerSize.setEnabled(True)
        self.PlotListLineWidth.setEnabled(True)
        self.populatePlotListOptions()

    def populatePlotListOptions(self):
        self.UpdatePlotList.setEnabled(False)
        selrows = 0
        self.PlotListColorSymbol.clear()
        self.PlotListColorBarHeader.clear()
        self.plotlistSymbol = []
        self.plotlistColor = []
        self.PlotListTitle.setText('')
        self.PlotListXAxisLabel.setText('')
        self.PlotListYAxisLabel.setText('')
        self.PlotListZAxisLabel.setText('')
        for i in range(self.PlotTree.topLevelItemCount()):
            if self.PlotTree.topLevelItem(i).isSelected():
                selrows = selrows + 1

        for i in range(self.PlotTree.topLevelItemCount()):
            if selrows > 1:
                self.PlotListColorBarHeader.setEnabled(False)
                self.PlotListColorBarName.setEnabled(False)
                self.PlotListColorBarLabel.setEnabled(False)
                self.PlotListTitle.setText('')
                self.PlotListXAxisLabel.setText('')
                self.PlotListYAxisLabel.setText('')
                self.PlotListZAxisLabel.setText('')
                self.PlotListColorBarHeader.clear()
                self.PlotListColorBarLabel.setText('')
            else:
                self.PlotListColorBarHeader.setEnabled(True)
                self.PlotListColorBarName.setEnabled(True)
                self.PlotListColorBarLabel.setEnabled(True)

            if self.PlotTree.topLevelItem(i).isSelected():
                ptitem = self.PlotTree.topLevelItem(i)
                index = ptitem.text(5)
                pl = self.plotList[i]
                if pl['plotType'] == 'Scatter':
                    self.PlotListZAxisLabel.setEnabled(False)
                    if pl['symbolCode']:
                        self.PlotListColorBarHeader.setEnabled(False)
                        self.PlotListColorBarName.setEnabled(False)
                        self.PlotListColorBarLabel.setEnabled(False)
                    if selrows == 1:
                        self.PlotListTitle.setText(pl['plotTitle'])
                        self.PlotListXAxisLabel.setText(pl['xlabel'])
                        self.PlotListYAxisLabel.setText(pl['ylabel'])
                        self.PlotListZAxisLabel.setEnabled(False)
                        self.PlotListBin.setEnabled(False)
                        self.PlotListBarWidth.setEnabled(False)
                        self.PlotListBarSpacing.setEnabled(False)
                        headers = self.tableList[pl['keyID']].model().getHeaderNames()
                        nsheaders = []
                        for header in headers:
                            if self.tableList[pl['keyID']].model().getDtype(header) != 'O':
                                nsheaders.append(header)
                        self.PlotListColorBarHeader.addItems(nsheaders)
                        self.PlotListColorBarName.addItems(maps)
                        index = self.PlotListColorBarHeader.findText(pl['colorMapHeader'])
                        self.PlotListColorBarHeader.setCurrentIndex(index)
                        index = self.PlotListColorBarName.findText(pl['colorMapName'])
                        self.PlotListColorBarName.setCurrentIndex(index)
                        self.PlotListColorBarLabel.setText(pl['colorbarLabel'])
                        self.PlotListMarkerSize.setValue(pl['markersize'])
                    counter = 0
                    for k,header in enumerate(pl['yAxisDataHeader']):
                        if not pl['symbolCode']:
                            item = QTreeWidgetItem()
                            self.plotlistSymbol.append(QComboBox())
                            self.plotlistColor.append(QComboBox())
                            self.plotlistSymbol[-1].addItems(plotsymb)
                            self.plotlistColor[-1].addItems(plotcolor)
                            item.setText(0,header)
                            item.setText(1,'All')
                            item.setText(4,pl['legend'][k])
                            item.setText(5,str(i))
                            item.setFlags(item.flags() | Qt.ItemIsSelectable | Qt.ItemIsEditable)
                            self.plotlistColor[-1].activated.connect(self.updatePlotList)
                            self.plotlistSymbol[-1].activated.connect(self.updatePlotList)
                            self.PlotListColorSymbol.addTopLevelItem(item)
                            self.PlotListColorSymbol.setItemWidget(item,2,self.plotlistColor[-1])
                            self.PlotListColorSymbol.setItemWidget(item,3,self.plotlistSymbol[-1])
                            if not pl['colorMap']:
                                index = self.plotlistColor[-1].findText(pl['color'][k])
                                self.plotlistColor[-1].setCurrentIndex(index)
                            index = self.plotlistSymbol[-1].findText(pl['marker'][k])
                            self.plotlistSymbol[-1].setCurrentIndex(index)
                        else:
                            uniquevals = pd.unique(self.tableList[pl['keyID']].model().getColumnData(header))
                            for j,val in enumerate(uniquevals):
                                item = QTreeWidgetItem()
                                self.plotlistSymbol.append(QComboBox())
                                self.plotlistColor.append(QComboBox())
                                self.plotlistSymbol[-1].addItems(plotsymb)
                                self.plotlistColor[-1].addItems(plotcolor)
                                item.setText(0,header)
                                item.setText(1,str(val))
                                item.setText(4,pl['legend'][counter])
                                item.setText(5,str(i))
                                item.setFlags(item.flags() | Qt.ItemIsSelectable | Qt.ItemIsEditable)
                                self.plotlistColor[-1].activated.connect(self.updatePlotList)
                                self.plotlistSymbol[-1].activated.connect(self.updatePlotList)
                                self.PlotListColorSymbol.addTopLevelItem(item)
                                self.PlotListColorSymbol.setItemWidget(item,2,self.plotlistColor[-1])
                                self.PlotListColorSymbol.setItemWidget(item,3,self.plotlistSymbol[-1])
                                if not pl['colorMap']:
                                    index = self.plotlistColor[-1].findText(pl['color'][counter])
                                    self.plotlistColor[-1].setCurrentIndex(index)
                                index = self.plotlistSymbol[-1].findText(pl['marker'][counter])
                                self.plotlistSymbol[-1].setCurrentIndex(index)
                                counter = counter + 1

                if pl['plotType'] == 'Pie':
                    if selrows == 1:
                        self.PlotListTitle.setText(pl['plotTitle'])
                        self.PlotListXAxisLabel.setText(pl['xlabel'])
                        self.PlotListYAxisLabel.setEnabled(False)
                        self.PlotListZAxisLabel.setEnabled(False)
                        self.PlotListColorBarHeader.setEnabled(False)
                        self.PlotListFontSize.setEnabled(False)
                        self.PlotListLineWidth.setEnabled(False)
                        self.PlotListColorBarName.setEnabled(False)
                        self.PlotListColorBarLabel.setEnabled(False)
                        self.PlotListMarkerSize.setEnabled(False)
                        self.PlotListBarWidth.setEnabled(False)
                        self.PlotListBarSpacing.setEnabled(False)
                    self.PlotListBin.setValue(pl['binNum'])

                if pl['plotType'] == 'Bar':
                    if selrows == 1:
                        self.PlotListTitle.setText(pl['plotTitle'])
                        self.PlotListXAxisLabel.setText(pl['xlabel'])
                        self.PlotListYAxisLabel.setText(pl['ylabel'])
                        self.PlotListZAxisLabel.setEnabled(False)
                        self.PlotListColorBarHeader.setEnabled(False)
                        self.PlotListFontSize.setEnabled(False)
                        self.PlotListLineWidth.setEnabled(False)
                        self.PlotListColorBarName.setEnabled(False)
                        self.PlotListColorBarLabel.setEnabled(False)
                        self.PlotListMarkerSize.setEnabled(False)
                    self.PlotListBarWidth.setValue(pl['barwidth'])
                    self.PlotListBarSpacing.setValue(pl['barspace'])

                if pl['plotType'] == 'Basemap':
                    if selrows == 1:
                        self.PlotListTitle.setText(pl['plotTitle'])
                        self.PlotListXAxisLabel.setText(pl['xlabel'])
                        self.PlotListYAxisLabel.setText(pl['ylabel'])
                        self.PlotListZAxisLabel.setEnabled(False)
                        self.PlotListBin.setEnabled(False)
                        self.PlotListBarWidth.setEnabled(False)
                        self.PlotListBarSpacing.setEnabled(False)
                        headers = self.tableList[pl['keyID']].model().getHeaderNames()
                        nsheaders = []
                        for header in headers:
                            if self.tableList[pl['keyID']].model().getDtype(header) != 'O':
                                nsheaders.append(header)
                        self.PlotListColorBarHeader.addItems(nsheaders)
                        self.PlotListColorBarName.addItems(maps)
                        index = self.PlotListColorBarHeader.findText(pl['colorMapHeader'])
                        self.PlotListColorBarHeader.setCurrentIndex(index)
                        index = self.PlotListColorBarName.findText(pl['colorMapName'])
                        self.PlotListColorBarName.setCurrentIndex(index)
                        self.PlotListColorBarLabel.setText(pl['colorbarLabel'])
                        self.PlotListMarkerSize.setValue(pl['markersize'])
                    item = QTreeWidgetItem()
                    self.plotlistSymbol.append(QComboBox())
                    self.plotlistColor.append(QComboBox())
                    self.plotlistSymbol[-1].addItems(plotsymb)
                    self.plotlistColor[-1].addItems(plotcolor)
                    item.setText(0,'Coordinates')
                    item.setText(1,'All')
                    item.setText(4,'N/A for this type')
                    item.setText(5,str(i))
                    item.setFlags(item.flags() | Qt.ItemIsSelectable | Qt.ItemIsEditable)
                    self.plotlistColor[-1].activated.connect(self.updatePlotList)
                    self.plotlistSymbol[-1].activated.connect(self.updatePlotList)
                    self.PlotListColorSymbol.addTopLevelItem(item)
                    self.PlotListColorSymbol.setItemWidget(item,2,self.plotlistColor[-1])
                    self.PlotListColorSymbol.setItemWidget(item,3,self.plotlistSymbol[-1])
                    if not pl['colorMap']:
                        index = self.plotlistColor[-1].findText(pl['color'])
                        self.plotlistColor[-1].setCurrentIndex(index)
                    index = self.plotlistSymbol[-1].findText(pl['marker'])
                    self.plotlistSymbol[-1].setCurrentIndex(index)

                if pl['plotType'] == '3D Plot':
                    if selrows == 1:
                        self.PlotListTitle.setText(pl['plotTitle'])
                        self.PlotListXAxisLabel.setText(pl['xlabel'])
                        self.PlotListYAxisLabel.setText(pl['ylabel'])
                        self.PlotListZAxisLabel.setText(pl['zlabel'])
                        self.PlotListBin.setEnabled(False)
                        self.PlotListBarWidth.setEnabled(False)
                        self.PlotListBarSpacing.setEnabled(False)
                        headers = self.tableList[pl['keyID']].model().getHeaderNames()
                        nsheaders = []
                        for header in headers:
                            if self.tableList[pl['keyID']].model().getDtype(header) != 'O':
                                nsheaders.append(header)
                        self.PlotListColorBarHeader.addItems(nsheaders)
                        self.PlotListColorBarName.addItems(maps)
                        index = self.PlotListColorBarHeader.findText(pl['colorMapHeader'])
                        self.PlotListColorBarHeader.setCurrentIndex(index)
                        index = self.PlotListColorBarName.findText(pl['colorMapName'])
                        self.PlotListColorBarName.setCurrentIndex(index)
                        self.PlotListColorBarLabel.setText(pl['colorbarLabel'])
                        self.PlotListMarkerSize.setValue(pl['markersize'])
                    item = QTreeWidgetItem()
                    self.plotlistSymbol.append(QComboBox())
                    self.plotlistColor.append(QComboBox())
                    self.plotlistSymbol[-1].addItems(plotsymb)
                    self.plotlistColor[-1].addItems(plotcolor)
                    item.setText(0,'Coordinates')
                    item.setText(1,'All')
                    item.setText(4,'N/A for this type')
                    item.setText(5,str(i))
                    item.setFlags(item.flags() | Qt.ItemIsSelectable | Qt.ItemIsEditable)
                    self.plotlistColor[-1].activated.connect(self.updatePlotList)
                    self.plotlistSymbol[-1].activated.connect(self.updatePlotList)
                    self.PlotListColorSymbol.addTopLevelItem(item)
                    self.PlotListColorSymbol.setItemWidget(item,2,self.plotlistColor[-1])
                    self.PlotListColorSymbol.setItemWidget(item,3,self.plotlistSymbol[-1])
                    if not pl['colorMap']:
                        index = self.plotlistColor[-1].findText(pl['color'])
                        self.plotlistColor[-1].setCurrentIndex(index)
                    index = self.plotlistSymbol[-1].findText(pl['marker'])
                    self.plotlistSymbol[-1].setCurrentIndex(index)
        self.UpdatePlotList.setEnabled(True)

    def updatePlotList(self):
        selrows = 0
        for i in range(self.PlotTree.topLevelItemCount()):
            if self.PlotTree.topLevelItem(i).isSelected():
                selrows = selrows + 1
        for i in range(self.PlotTree.topLevelItemCount()):
            if self.PlotTree.topLevelItem(i).isSelected():
                pl = self.plotList[i]
                if pl['plotType'] == 'Scatter':
                    color = []
                    marker = []
                    legend = []
                    if selrows == 1:
                        pl['xlabel'] = self.PlotListXAxisLabel.text()
                        pl['ylabel'] = self.PlotListYAxisLabel.text()
                        pl['plotTitle'] = self.PlotListTitle.text()
                        if pl['colorMap'] or self.PlotListColorBarHeader.currentText() != '':
                            pl['colorMap'] = plt.cm.get_cmap(self.PlotListColorBarName.currentText())
                            pl['colorMapHeader'] = self.PlotListColorBarHeader.currentText()
                            pl['colorMapName'] = self.PlotListColorBarName.currentText()
                            pl['colorbarLabel'] = self.PlotListColorBarLabel.text()
                            for k in range(len(pl['ydata'])):
                                color.append(self.tableList[pl['keyID']].model().getColumnData(self.PlotListColorBarHeader.currentText()))
                    for j in range(self.PlotListColorSymbol.topLevelItemCount()):
                        item = self.PlotListColorSymbol.topLevelItem(j)
                        if item.text(5) == str(i):
                            if not pl['colorMap']:
                                color.append(self.plotlistColor[j].currentText())
                            marker.append(self.plotlistSymbol[j].currentText())
                            legend.append(item.text(4))
                    pl['markersize'] = self.PlotListMarkerSize.value()
                    pl['color'] = color
                    pl['marker'] = marker
                    pl['legend'] = legend

                if pl['plotType'] == 'Pie':
                    if selrows == 1:
                        pl['xlabel'] = self.PlotListXAxisLabel.text()
                        pl['plotTitle'] = self.PlotListTitle.text()
                    binnum = int(self.PlotListBin.value())
                    x = self.tableList[pl['keyID']].model().getColumnData(pl['xAxisDataHeader'])
                    if len(pd.unique(x)) > 20 and x.dtype.kind != 'O':
                        bins = np.linspace(x.min(),x.max(),binnum+1)
                        y = pd.cut(x,bins)
                        counts = y.value_counts().sort_index()
                        cmap = plt.cm.jet
                        colors = cmap(np.linspace(0., 1., binnum))
                    else:
                        u = len(pd.unique(x))
                        cmap = plt.cm.jet
                        colors = cmap(np.linspace(0.,1.,u))
                        counts = x.value_counts().sort_index()
                    pl['xdata'] = counts
                    pl['binNum'] = binnum
                    pl['color'] = colors
                    pl['legend'] = counts.index

                if pl['plotType'] == 'Bar':
                    if selrows == 1:
                        pl['xlabel'] = self.PlotListXAxisLabel.text()
                        pl['ylabel'] = self.PlotListYAxisLabel.text()
                        pl['plotTitle'] = self.PlotListTitle.text()
                    x = self.tableList[pl['keyID']].model().getColumnData(pl['xAxisDataHeader'])
#                    if len(pd.unique(x)) > 100:
#                    return
                    spacing = [j*(self.PlotListBarSpacing.value()) for j in range(len(pd.unique(x)))]
                    pl['spacing'] = spacing
                    pl['barspace'] = self.PlotListBarSpacing.value()
                    pl['barwidth'] = self.PlotListBarWidth.value()
                    pl['xdata'] = x.value_counts()
                    pl['color'] = 'blue'
                    pl['legend'] = x.value_counts().index

                if pl['plotType'] == 'Basemap':
                    if selrows == 1:
                        pl['xlabel'] = self.PlotListXAxisLabel.text()
                        pl['ylabel'] = self.PlotListYAxisLabel.text()
                        pl['plotTitle'] = self.PlotListTitle.text()
                        if pl['colorMap'] or self.PlotListColorBarHeader.currentText() != '':
                            pl['colorMap'] = plt.cm.get_cmap(self.PlotListColorBarName.currentText())
                            pl['colorMapHeader'] = self.PlotListColorBarHeader.currentText()
                            pl['colorMapName'] = self.PlotListColorBarName.currentText()
                            pl['colorbarLabel'] = self.PlotListColorBarLabel.text()
                            color = self.tableList[pl['keyID']].model().getColumnData(self.PlotListColorBarHeader.currentText())
                            print(color)
                    for j in range(self.PlotListColorSymbol.topLevelItemCount()):
                        item = self.PlotListColorSymbol.topLevelItem(j)
                        if item.text(5) == str(i):
                            if not pl['colorMap']:
                                color = self.plotlistColor[j].currentText()
                            marker = self.plotlistSymbol[j].currentText()
                            legend = item.text(4)
                    pl['markersize'] = self.PlotListMarkerSize.value()
                    pl['color'] = color
                    pl['marker'] = marker
                    pl['legend'] = legend

                if pl['plotType'] == '3D Plot':
                    if selrows == 1:
                        pl['xlabel'] = self.PlotListXAxisLabel.text()
                        pl['ylabel'] = self.PlotListYAxisLabel.text()
                        pl['zlabel'] = self.PlotListZAxisLabel.text()
                        pl['plotTitle'] = self.PlotListTitle.text()
                        if pl['colorMap'] or self.PlotListColorBarHeader.currentText() != '':
                            pl['colorMap'] = plt.cm.get_cmap(self.PlotListColorBarName.currentText())
                            pl['colorMapHeader'] = self.PlotListColorBarHeader.currentText()
                            pl['colorMapName'] = self.PlotListColorBarName.currentText()
                            pl['colorbarLabel'] = self.PlotListColorBarLabel.text()
                            color = self.tableList[pl['keyID']].model().getColumnData(self.PlotListColorBarHeader.currentText())
                    for j in range(self.PlotListColorSymbol.topLevelItemCount()):
                        item = self.PlotListColorSymbol.topLevelItem(j)
                        if item.text(5) == str(i):
                            if not pl['colorMap']:
                                color = self.plotlistColor[j].currentText()
                            marker = self.plotlistSymbol[j].currentText()
                    pl['markersize'] = self.PlotListMarkerSize.value()
                    pl['color'] = color
                    pl['marker'] = marker
        return

    def plotFigures(self):
        if self.PlotTree.currentIndex():
            for i in range(self.PlotTree.topLevelItemCount()):
                if self.PlotTree.topLevelItem(i).isSelected():
                    pl = self.plotList[i]
                    fig,ax = plt.subplots()
                    if pl['plotType'] == 'Scatter':
                        for j,ydat in enumerate(pl['ydata']):
                            if pl['symbolCode']:
                                sc = ax.scatter(pl['xdata'][j], ydat, s = pl['markersize'],
                                    c = pl['color'][j], cmap = pl['colorMap'], marker = pl['marker'][j], label = pl['legend'][j])
                            else:
                                sc = ax.scatter(pl['xdata'][0], ydat, s = pl['markersize'],
                                    c = pl['color'][j], cmap = pl['colorMap'], marker = pl['marker'][j], label = pl['legend'][j])
                        ax.legend().draggable()
                        ax.set_title(pl['plotTitle'])
                        ax.set_xlabel(pl['xlabel'])
                        ax.set_ylabel(pl['ylabel'])
                        if pl['colorMap']:
                            fig.colorbar(sc).set_label(pl['colorbarLabel'])
                        ax.set_aspect('auto')

                    if pl['plotType'] == 'Pie':
                        ax.pie(pl['xdata'], autopct = '%.2f',colors = pl['color'])
                        ax.legend(pl['legend']).draggable()
                        ax.set_title(pl['plotTitle'])
                        ax.set_xlabel(pl['xlabel'])
                        ax.set_aspect('equal')

                    if pl['plotType'] == 'Bar':
                        ax.bar(pl['spacing'],pl['xdata'],pl['barwidth'],tick_label = pl['legend'])
                        ax.set_title(pl['plotTitle'])
                        ax.set_xlabel(pl['xlabel'])
                        ax.set_ylabel(pl['ylabel'])
                        ax.set_aspect('auto')

                    if pl['plotType'] == 'Basemap':
                        ax = plt.axes(projection=ccrs.PlateCarree())
                        ax.add_feature(cartopy.feature.COASTLINE)
                        ax.add_feature(cartopy.feature.BORDERS)
                        ax.add_feature(cartopy.feature.LAND)
                        ax.add_feature(cartopy.feature.OCEAN)
                        sc = ax.scatter(pl['xdata'], pl['ydata'], s = pl['markersize'],
                                        c = pl['color'], cmap = pl['colorMap'], marker = pl['marker'], transform=pl['projection'])
                        if pl['colorMap']:
                            fig.colorbar(sc).set_label(pl['colorbarLabel'])
                        ax.set_aspect('auto')
                        ax.set_adjustable('datalim')

                    if pl['plotType'] == '3D Plot':
                        ax = Axes3D(fig)
                        sc = ax.scatter(pl['xdata'], pl['ydata'], pl['zdata'], zdir = 'z', s = pl['markersize'],
                                        c = pl['color'], cmap = pl['colorMap'], marker = pl['marker'])
                        ax.set_title(pl['plotTitle'])
                        ax.set_xlabel(pl['xlabel'])
                        ax.set_ylabel(pl['ylabel'])
                        ax.set_zlabel(pl['zlabel'])
                        if pl['colorMap']:
                            fig.colorbar(sc).set_label(pl['colorbarLabel'])
                        ax.set_aspect('auto')
                    ax.figure.tight_layout()
                    plt.ion()
                    plt.show()
                    plt.ioff()
        return


    def Calc(self):
        self.queue = queue.Queue()
        self.thread.append(SimpleThread(self.queue, self.addOutsideData,lf.calcPI,self,np.sqrt(2),2000000))
#        self.thread.append(Worker(lf.calcpi,self,2,2**(.25),20000))
        self.thread[-1].start()

    def addOutsideData(self,data):
        keyID = 'Outside/piCalc'
        data = data.val
        self.MasterData[keyID] = {'SelH':list(data.keys()),
                                   'AllH':list(data.keys()),
                                   'AddH':[],
                                   'AddData':{},
                                   'Path':'Outside',
                                   'Filename':'outside',
                                   'Group':'picalc',
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
        self.tableList[keyID].selectionModel().selectionChanged.connect(self.setupPlotOptions)
        self.addNativeHeaders()
        self.initPlotOptions()
        self.TableTab.blockSignals(False)
        self.headermenu = self.tableList[keyID].horizontalHeader()
        self.headermenu.setContextMenuPolicy(Qt.CustomContextMenu)
        self.headermenu.customContextMenuRequested.connect(self.headerPopup)


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
        return False
        if role == QtCore.Qt.EditRole:
            row = index.row()
            column = index.column()
            print(type(self.arraydata[self.header[column]][row]))
            #return False
            #if isinstance(self.arraydata[self.header[column]][row],bytes):
            #    value = value.encode("utf-8")
            #dtype = self.arraydata[self.header[column]][row].dtype.kind
            #value = value.toPyObject()
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
#            if isinstance(value,bytes):
#                return value.decode("utf-8")
#            else:
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

    def getHeaderNames(self):
        return self.header

    def filterTable(self,procedures=[]):
        self.arraydata = copy.deepcopy(self.DataOrig)
        self.procedures = procedures
        sort = False
        OrFilt = False
        sortAD = []
        sortheader = []
        orcheckdict = dict((key,[]) for key in orkeys)
        for i in range(len(self.procedures)):
            header = self.procedures[i][0]
            sortby = self.procedures[i][1]
            value = self.procedures[i][2]
            orcheck = self.procedures[i][3]
            orchecks = False
            dtype = self.arraydata[header].dtype
            if 'Order' not in sortby:
                if dtype == 'O':
                    if 'Range' in sortby and ':' in value:
                        valueLower,valueUpper = value.split(':')
                        if valueLower == '':
                            valueLower = ''
                        if valueUpper == '':
                            valueUpper = ''
                    elif 'Range' in sortby:
                        print('There is no ":" in the value for the In Range filter')
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
                            print(valueLower + ' ' + valueUpper + ': One of these values cannot be of type bool')
                            continue
                    elif 'Range' in sortby:
                        print('There is no ":" in the value for the In Range filter')
                        continue
                    else:
                        try:
                            value = bool(value)
                        except:
                            print(value + ' cannot be of type bool')
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
                            print(valueLower + ' ' + valueUpper + ': One of these values cannot be of type float')
                            continue
                    elif 'Range' in sortby:
                        print('There is no ":" in the value for the In Range filter')
                        continue
                    else:
                        if 'With' in sortby:
                            try:
                                value = int(value)
                            except:
                                print(value + ' cannot be of type int')
                        else:
                            try:
                                value = float(value)
                            except:
                                print(value + ' cannot be of type float')
                                continue
            if orcheck != '':
                orchecks = True
                OrFilt = True
            if sortby == 'Less Than':
                if orchecks:
                    orcheckdict[orcheck].append(self.arraydata[header]<value)
                else:
                    self.arraydata = self.arraydata[self.arraydata[header]<value]
            if sortby == 'Greater Than':
                if orchecks:
                    orcheckdict[orcheck].append(self.arraydata[header]>value)
                else:
                    self.arraydata = self.arraydata[self.arraydata[header]>value]
            if sortby == 'Equal To':
                if orchecks:
                    orcheckdict[orcheck].append(self.arraydata[header]==value)
                else:
                    self.arraydata = self.arraydata[self.arraydata[header]==value]
            if sortby == 'Not Equal To':
                if orchecks:
                    orcheckdict[orcheck].append(self.arraydata[header]!=value)
                else:
                    self.arraydata = self.arraydata[self.arraydata[header]!=value]
            if sortby == 'In Range':
                if orchecks:
                    orcheckdict[orcheck].append(self.arraydata[header].between(valueLower,valueUpper))
                else:
                    self.arraydata = self.arraydata[self.arraydata[header].between(valueLower,valueUpper)]
            if sortby == 'Not In Range':
                if orchecks:
                    orcheckdict[orcheck].append(~self.arraydata[header].between(valueLower,valueUpper))
                else:
                    self.arraydata = self.arraydata[~self.arraydata[header].between(valueLower,valueUpper)]
            if sortby == 'Starts With':
                if orchecks:
                    orcheckdict[orcheck].append(self.arraydata[header].astype(str).str.lower().str.startswith(str(value)))
                else:
                    self.arraydata = self.arraydata[self.arraydata[header].astype(str).str.lower().str.startswith(str(value))]
            if sortby == 'Does Not Start With':
                if orchecks:
                    orcheckdict[orcheck].append(~self.arraydata[header].astype(str).str.lower().str.startswith(str(value)))
                else:
                    self.arraydata = self.arraydata[~self.arraydata[header].astype(str).str.lower().str.startswith(str(value))]
            if sortby == 'Ends With':
                if orchecks:
                    orcheckdict[orcheck].append(self.arraydata[header].astype(str).str.lower().str.endswith(str(value)))
                else:
                    self.arraydata = self.arraydata[self.arraydata[header].astype(str).str.lower().str.endswith(str(value))]
            if sortby == 'Does Not End With':
                if orchecks:
                    orcheckdict[orcheck].append(~self.arraydata[header].astype(str).str.lower().str.endswith(str(value)))
                else:
                    self.arraydata = self.arraydata[~self.arraydata[header].astype(str).str.lower().str.endswith(str(value))]
            if sortby == 'Contains':
                if orchecks:
                    orcheckdict[orcheck].append(self.arraydata[header].astype(str).str.lower().str.contains(str(value),case=False))
                else:
                    self.arraydata = self.arraydata[self.arraydata[header].astype(str).str.lower().str.contains(str(value),case=False)]
            if sortby == 'Does Not Contain':
                if orchecks:
                    orcheckdict[orcheck].append(~self.arraydata[header].astype(str).str.lower().str.contains(str(value),case=False))
                else:
                    self.arraydata = self.arraydata[~self.arraydata[header].astype(str).str.lower().str.contains(str(value),case=False)]
            if sortby == 'Ascending Order':
                sort = True
                sortAD.append(True)
                sortheader.append(header)
            if sortby == 'Descending Order':
                sort = True
                sortAD.append(False)
                sortheader.append(header)
        if OrFilt:
            idxs = pd.Series(np.array([True]*self.arraydata.shape[0]))
            for key in orcheckdict:
                if orcheckdict[key]:
                    oridxs = pd.Series(np.array([False]*self.arraydata.shape[0]))
                    for idxo in orcheckdict[key]:
                        oridxs = oridxs | idxo
                    idxs = idxs & oridxs
            self.arraydata.reset_index(inplace=True, drop=True)
            self.arraydata = self.arraydata[idxs]
        if sort:
            self.arraydata = self.arraydata.sort_values(by=sortheader,ascending=sortAD)
        self.arraydata.reset_index(inplace=True, drop=True)
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