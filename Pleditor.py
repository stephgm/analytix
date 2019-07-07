# -*- coding: utf-8 -*-
"""
Created on Tue Jun 11 14:16:07 2019

@author: DivollHJ
"""
import os
import sys
import pandas as pd
if sys.version_info.major == 2:
    import cPickle
else:
    import pickle as cPickle
import numpy as np
from glob import glob
from collections import OrderedDict
import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui
import PyQt5.QtGui as QtWidgets
from PyQt5.Qt import *
from PyQt5 import QtSql
from PyQt5.QtCore import QVariant
from PyQt5 import QtSql, uic#, QtOpenGL
import copy
import Plotterator as plrt
import matplotlib
from functools import reduce
import operator
import re
from matplotlib.backends.backend_qt5agg import (FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
colors = dict(matplotlib.colors.BASE_COLORS, **matplotlib.colors.CSS4_COLORS)
by_hsv = sorted((tuple(matplotlib.colors.rgb_to_hsv(matplotlib.colors.to_rgba(color)[:3])), name)
                for name, color in colors.items())
mplcolors = [name for hsv, name in by_hsv]
mplsymbols = filter(lambda i:(((type(i) is unicode) or (type(i) is str)) and (i != 'None') and i),matplotlib.markers.MarkerStyle.markers.keys())
mplcmaps = sorted(m for m in matplotlib.pyplot.cm.datad if not m.endswith("_r"))
mpllines = matplotlib.lines.lineStyles.keys()
TRANSFORMS = ['PlateCarree()','NorthPolarStereo()','EckertV()','RotatedPole()','Orthographic()']
mplpatches = ['Circle','Ellipse','Polygon','Rectangle']
intvalidator = QtGui.QIntValidator()
doublevalidator = QtGui.QDoubleValidator()


class getCommand(QDialog):
    def __init__(self,items,parent=None):
        super(getCommand,self).__init__(parent)
        self.layouts = QVBoxLayout()
        self.listwidget = QListWidget()
        self.Okay = QPushButton('OK')
        self.listwidget.addItems(items)
        self.layouts.addWidget(self.listwidget)
        self.layouts.addWidget(self.Okay)
        self.setLayout(self.layouts)
        self.Okay.clicked.connect(self.Accept)
        
        
    def Accept(self):
        self.close()
        
def getSelectedItems(items):
    widget = getCommand(items)
    widget.exec_()
    try:
        return widget.listwidget.currentItem().text()
    except:
        return ''

class getLabel(QDialog):
    def __init__(self,parent=None):
        super(getLabel, self).__init__(parent)
        self.layouts = QVBoxLayout()
        self.label = QLabel('Enter Kwarg Name')
        self.line = QLineEdit()
        self.Okay = QPushButton('OK')
        self.layouts.addWidget(self.label)
        self.layouts.addWidget(self.line)
        self.layouts.addWidget(self.Okay)
        self.Okay.clicked.connect(self.Accept)
        self.setLayout(self.layouts)
    
    def Accept(self):
        self.close()
#        return self.line.text()

def getlabel():
    widget = getLabel()
    widget.exec_()
    return widget.line.text()


noshow_dict = {'plot':['x','y','plottype'],
               'scatter':['x','y','plottype'],
               'pie':['x','plottype'],
               'scatter3d':['x','y','z','plottype'],
               'stackplot':['x','y','plottype'],
               'hist':['x','bins','plottype'],
               'bar':['x','height','plottype'],
               'barh':['x','width','plottype'],
               }
noshow_keys = ['lines','cbs']
noshow_attributes = ['x','y','z','bins','height','width','plottype','stylesheet','customlegend'\
                     'table','3d','mapplot','customlegend','combinelegend']
class Pleditor(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        uic.loadUi('Pleditor.ui', self)
        self.makeConnections()
        self.dynamic_canvas = FigureCanvas(matplotlib.figure.Figure())
        self.CanvasLayout.addWidget(self.dynamic_canvas)
        self.dynamic_canvas.figure.subplots()
        self.isValid = True
        self.fname = ''
        self.timer = QTimer()
        self.timer.setInterval(5000)
        self.timer.start()
        self.timer.timeout.connect(lambda:self.Alert(''))
    
    def warningBox(self,msg,detail):
        box = QMessageBox()
        box.setIcon(QMessageBox.Warning)
        box.setText(msg)
        box.setDetailedText(detail)
        box.setWindowTitle('Warning')
        box.setStandardButtons(QMessageBox.Ok)
        force = box.addButton('Save Anyways',QMessageBox.YesRole)
        retval = box.exec_()
        
        if box.clickedButton() == force:
            self.save(override=True)
        
    def Alert(self,msg):
        self.timer.setInterval(5000)
        self.timer.start()
        self.statusbar.showMessage(msg)
    
    def makeConnections(self):
        self.OpenButton.clicked.connect(self.openFile)
        self.PreviewButton.clicked.connect(self.preview)
        self.SaveButton.clicked.connect(self.save)

    def openFile(self):
        self.fname = ''
        self.fname = QFileDialog.getOpenFileName(self, 'Open File',os.getcwd(),'pickle plot (*.pklplt)')[0]
        if self.fname:
            self.Alert('Loading the Plot')
            self.plotDict = cPickle.load(file(self.fname,'rb'))
            self.setupTreeWidget(None,self.plotDict)
            self.preview()
            self.Alert('Done Loading')
            
    def preview(self):
        old = self.dynamic_canvas.figure
        
        try:
            if self.fname:
                for i in reversed(range(self.CanvasLayout.count())):
                    widgetToRemove = self.CanvasLayout.itemAt(i).widget()
                    self.CanvasLayout.removeWidget(widgetToRemove)
                    widgetToRemove.deleteLater()
                self.dynamic_canvas = FigureCanvas(matplotlib.figure.Figure())
                pltr = plrt.Plotter()
                pltr.sub = self.plotDict['sub']
                pltr.fig = self.plotDict['fig']
                myfig,myax = pltr.createPlot('',RETURN=True)
                self.CanvasLayout.addWidget(NavigationToolbar(self.dynamic_canvas,self))
                self.CanvasLayout.addWidget(self.dynamic_canvas)
                #Get the damn legend to move?
                self.dynamic_canvas.figure = myfig
                self.isValid = True
        except:
            for i in reversed(range(self.CanvasLayout.count())):
                    widgetToRemove = self.CanvasLayout.itemAt(i).widget()
                    self.CanvasLayout.removeWidget(widgetToRemove)
                    widgetToRemove.deleteLater()
            self.dynamic_canvas = FigureCanvas(matplotlib.figure.Figure())
            self.dynamic_canvas.figure = old
            self.CanvasLayout.addWidget(self.dynamic_canvas)
            self.isValid = False
            self.Alert('Whatever you just did invalidated the plot.')
    
    def save(self,override=False):
        if self.fname and (self.isValid or override):
            newfname = self.fname.strip('.pklplt')
            pltr = plrt.Plotter()
            pltr.sub = self.plotDict['sub']
            pltr.fig = self.plotDict['fig']
            if override:
                pltr.savePkl(newfname+'_INVALID.pklplt')
            else:
                pltr.createPlot(newfname+'_Edited.pklplt',SAVE=True,SAVEPKL=True)
            self.Alert(newfname+' was saved!')
        else:
            msg = 'Warning: The plot you are trying to save is invalid.\nThe plot will not be saved'
            detail = 'Please check that all args and kwargs are correct.\n Visit https://matplotlib.org/ for assistance'
            
            self.warningBox(msg,detail)
            
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
            self.Alert('The color widget is not a QLineEdit')
    
    def filepicker(self,widget,ext):
        name = QFileDialog.getOpenFileName(self, 'Open File',os.getcwd(),'Files;(*.'+ext+')')[0]
        if name:
            widget.setText(name)
    
    def setupTreeWidget(self,widget,treedata):
        """
        worst case -> sub[(0,0)]['commands'][0]['kwargs']['prop']['size'] = 6
        """
        treedata = copy.deepcopy(treedata)
        treedata = OrderedDict(treedata.items())
        self.PlotTabWidget.clear()
#        self.PlotOptionsTree.clear()
#        widget.blockSignals(True)
        self.nestedwidgets = {key:{} for key in treedata.keys()}
        def walkDict(d,parent,dkeymap):
#            if not parent:
            if len(dkeymap) == 1 and 'fig' in dkeymap:
                tablewidget = QWidget()
                tablelayout = QGridLayout()
                self.currentTreeWidget = QTreeWidget()
                self.currentTreeWidget.setSizeAdjustPolicy(self.currentTreeWidget.AdjustToContents)
                self.currentTreeWidget.header().hide()
                self.currentTreeWidget.setVerticalScrollMode(self.currentTreeWidget.ScrollPerPixel)
                tablelayout.addWidget(self.currentTreeWidget)
                tablewidget.setLayout(tablelayout)
                self.PlotTabWidget.addTab(tablewidget,'fig')
                self.parent = QTreeWidgetItem(self.currentTreeWidget)
            elif len(dkeymap) == 2 and isinstance(dkeymap[1],tuple):
                self.currentTreeWidget.expandAll()
                tablewidget = QWidget()
                tablelayout = QGridLayout()
                self.OGLinesTW = QTreeWidget()
                self.currentTreeWidget = self.OGLinesTW
                self.currentTreeWidget.header().hide()
                self.currentTreeWidget.setSizeAdjustPolicy(self.currentTreeWidget.AdjustToContents)
                self.currentTreeWidget.setVerticalScrollMode(self.currentTreeWidget.ScrollPerPixel)
                self.CurrentLineTab = QTabWidget()
                tablelayout.addWidget(self.CurrentLineTab)
                ltwidget = QWidget()
                ltlayout = QGridLayout()
                ltlayout.addWidget(self.currentTreeWidget)
                ltwidget.setLayout(ltlayout)
                self.CurrentLineTab.addTab(ltwidget,'Line Data')
                tablewidget.setLayout(tablelayout)
                self.PlotTabWidget.addTab(tablewidget,str(dkeymap[1]))
                self.parent = QTreeWidgetItem(self.currentTreeWidget)
#            widget = self.currentTreeWidget
            else:
                self.parent = parent
#            widget = self.currentTreeWidget
            key = dkeymap[0]
            d = OrderedDict(d)
            for k, v in d.iteritems():
                if k in ['patches','commands'] and len(dkeymap) > 1 and isinstance(dkeymap[1],tuple):
                    self.currentTreeWidget.expandAll()
                    cpwidget = QWidget()
                    cplayout = QGridLayout()
                    self.currentTreeWidget = QTreeWidget()
                    self.currentTreeWidget.header().hide()
                    self.currentTreeWidget.setSizeAdjustPolicy(self.currentTreeWidget.AdjustToContents)
                    self.currentTreeWidget.setVerticalScrollMode(self.currentTreeWidget.ScrollPerPixel)
                    cplayout.addWidget(self.currentTreeWidget)
                    cpwidget.setLayout(cplayout)
                    self.CurrentLineTab.addTab(cpwidget,k)
                    self.parent = QTreeWidgetItem(self.currentTreeWidget)
                elif len(dkeymap) > 1 and len(dkeymap)==2 and isinstance(dkeymap[1],tuple):
                    self.currentTreeWidget = self.OGLinesTW
                    self.currentTreeWidget.header().hide()
                    self.currentTreeWidget.setSizeAdjustPolicy(self.currentTreeWidget.AdjustToContents)
                    self.currentTreeWidget.setVerticalScrollMode(self.currentTreeWidget.ScrollPerPixel)
                    self.parent = QTreeWidgetItem(self.currentTreeWidget)
                    
                unalteredk = copy.copy(k)
                ogtype = type(v)
                if isinstance(v,float):
                    validator = doublevalidator
                elif isinstance(v,int):
                    validator = intvalidator
                else:
                    validator = None
                if k in noshow_attributes:
                    continue
                if not isinstance(k,str):
                    k = str(k)
                if isinstance(v,list) and len(v):
                    child = QTreeWidgetItem(self.parent)
                    child.setText(0,k)
                else:
                    child = QTreeWidgetItem(self.parent)
                    child.setText(0,k)
                if isinstance(v, dict) and k not in ['commands']:
                    child.setFlags(child.flags())
                    nkeymap = copy.copy(dkeymap)
                    nkeymap.append(unalteredk)
                    if v:
                        v = walkDict(v,child,nkeymap)
                    else:
                        self.parent.removeChild(child)
                        continue
                elif k in ['mapimg']:
                    layout = QHBoxLayout()
                    filepicker = QPushButton('Select File')
                    le = QLineEdit(str(v))
                    le.setValidator(validator)
                    filepicker.clicked.connect(lambda trash,plwidget=le:self.filepicker(plwidget,'png'))
                    le.textChanged.connect(lambda trash, plwidget=le,plkey=key,pldictkey=k,plkeymap=dkeymap,vtype=str:self.updateDict(plwidget,plkey,pldictkey,plkeymap,vtype))
                    le.setReadOnly(True)
                    layout.addWidget(filepicker)
                    layout.addWidget(le)
                    self.nestedwidgets[key][k] = QWidget()
                    self.nestedwidgets[key][k].setLayout(layout)
                    grandchild = QTreeWidgetItem(child)
                    self.currentTreeWidget.setItemWidget(grandchild,0,self.nestedwidgets[key][k])
                elif k in ['facecolor']:
                    self.nestedwidgets[key][k]=QWidget()
                    layout = QHBoxLayout()
                    colorpickerbutton = QPushButton('Change Facecolor')
                    colorvalue = QLineEdit(v)
                    colorvalue.setValidator(validator)
                    colorpickerbutton.clicked.connect(lambda trash,plwidget=colorvalue:self.colorPicker(plwidget))
                    colorvalue.textChanged.connect(lambda trash, plwidget=colorvalue,plkey=key,pldictkey=k,plkeymap=dkeymap,vtype=ogtype:self.updateDict(plwidget,plkey,pldictkey,plkeymap,vtype))
                    layout.addWidget(colorpickerbutton)
                    layout.addWidget(colorvalue)
                    self.nestedwidgets[key][k].setLayout(layout)
                    grandchild = QTreeWidgetItem(child)
                    self.currentTreeWidget.setItemWidget(grandchild,0,self.nestedwidgets[key][k])
                elif k in ['cmap','picker','marker','mapproj','transform','ls','linestyle']:
                    if isinstance(d[k],np.ndarray) or isinstance(d[k],pd.DataFrame) or isinstance(d[k],pd.Series):
                        self.parent.removeChild(child)
                        continue
                    if not d[k]:
                        self.parent.removeChild(child)
                        continue
                    self.nestedwidgets[key][k] = QComboBox()
                    grandchild = QTreeWidgetItem(child)
                    if k == 'cmap':
                        self.nestedwidgets[key][k].addItems(mplcmaps)
                    elif k == 'picker':
                        self.nestedwidgets[key][k].addItems(['True','False'])
                    elif k == 'marker':
                        self.nestedwidgets[key][k].addItems(mplsymbols)
                    elif k in ['mapproj','transform']:
                        self.nestedwidgets[key][k].addItems(TRANSFORMS)
                    elif k in ['ls','linestyle']:
                        self.nestedwidgets[key][k].addItems(mpllines)
                    index = self.nestedwidgets[key][k].findText(str(v))
                    self.nestedwidgets[key][k].setCurrentIndex(index)
                    self.currentTreeWidget.setItemWidget(grandchild,0,self.nestedwidgets[key][k])
                    self.nestedwidgets[key][k].currentIndexChanged.connect(lambda trash, plwidget=self.nestedwidgets[key][k],plkey=key,pldictkey=k,plkeymap=dkeymap,vtype=ogtype:self.updateDict(plwidget,plkey,pldictkey,plkeymap,vtype))
                elif k in ['c','colors','color']:
                    if isinstance(d[k],np.ndarray) or isinstance(d[k],pd.DataFrame) or isinstance(d[k],pd.Series):
                        self.parent.removeChild(child)
                        continue
                    if not d[k]:
                        self.parent.removeChild(child)
                        continue
                    self.nestedwidgets[key][k] = []
                    if isinstance(v,list):
                        for i,item in enumerate(v):
                            self.nestedwidgets[key][k].append(QComboBox())
                            grandchild = QTreeWidgetItem(child)
                            self.nestedwidgets[key][k][-1].addItems(mplcolors)
                            index = self.nestedwidgets[key][k][-1].findText(str(item))
                            self.nestedwidgets[key][k][-1].setCurrentIndex(index)
                            self.currentTreeWidget.setItemWidget(grandchild,0,self.nestedwidgets[key][k][-1])
                            self.nestedwidgets[key][k][-1].currentIndexChanged.connect(lambda trash,plwidget=self.nestedwidgets[key][k][-1],pldictkey=k,plkeymap=dkeymap,index=i,vtype=str:self.handleList(plwidget,pldictkey,plkeymap,index,vtype))
                    else:
                        self.nestedwidgets[key][k] = QComboBox()
                        grandchild = QTreeWidgetItem(child)
                        self.nestedwidgets[key][k].addItems(mplcolors)
                        index = self.nestedwidgets[key][k].findText(str(v))
                        self.nestedwidgets[key][k].setCurrentIndex(index)
                        self.currentTreeWidget.setItemWidget(grandchild,0,self.nestedwidgets[key][k])
                        self.nestedwidgets[key][k].currentIndexChanged.connect(lambda trash, plwidget=self.nestedwidgets[key][k],plkey=key,pldictkey=k,plkeymap=dkeymap,vtype=ogtype:self.updateDict(plwidget,plkey,pldictkey,plkeymap,vtype))
                elif k in ['figsize']:
                    self.nestedwidgets[key][k] = []
                    j = 0
                    for item,coord in zip(v,['x figsize','y figsize']):
                        self.nestedwidgets[key][k].append(QWidget())
                        layout = QHBoxLayout()
                        label = QLabel(coord)
                        le = QLineEdit(str(item))
                        le.setValidator(doublevalidator)
                        layout.addWidget(label)
                        layout.addWidget(le)
                        self.nestedwidgets[key][k][-1].setLayout(layout)
                        le.editingFinished.connect(lambda plkeymap=dkeymap,plkey=k,idx=j,plwidget=le:self.handleList(plwidget,plkey,plkeymap,idx,float))
#                        le.setValidator(doublevalidator)
                        grandchild = QTreeWidgetItem(child)
                        self.currentTreeWidget.setItemWidget(grandchild,0,self.nestedwidgets[key][k][-1])
                        j+=1
                elif k in ['rowspan','colspan','zorder','s']:
                    le = QLineEdit(str(v))
                    le.setValidator(validator)
                    le.textChanged.connect(lambda trash, plwidget=le,plkey=key,pldictkey=k,plkeymap=dkeymap,vtype=ogtype:self.updateDict(plwidget,plkey,pldictkey,plkeymap,vtype))
                    self.nestedwidgets[key][k] = le
                    grandchild = QTreeWidgetItem(child)
                    self.currentTreeWidget.setItemWidget(grandchild,0,self.nestedwidgets[key][k])
                elif k in ['table']:
                    self.parent.removeChild(child)
                    continue
                elif k in ['commands']:
                    self.nestedwidgets[key][k]=[]
                    totallayout = QVBoxLayout()
                    totalwidget = QWidget()
                    if d[k]:
                        #cmd is list of commands
                        for cmd in d[k]:
                            toplevellayout = QGridLayout()
                            toplevellayout.addWidget(QLabel('Command'),0,0)
                            toplevellayout.addWidget(QLabel('Args'),0,1)
                            toplevellayout.addWidget(QLabel('Kwargs'),0,2)
                            nwidget = QWidget()
                            commandname = QLineEdit(cmd['cmd'])
                            commandname.setValidator(None)
                            commandargs = QListWidget()
                            commandname.editingFinished.connect(lambda plkeymap=dkeymap,plwidget=totalwidget,pldictkey=k:self.rebuildCommands(plkeymap,plwidget,pldictkey))
                            for arg in cmd['args']:
                                if isinstance(arg,float):
                                    argvalidator = doublevalidator
                                elif isinstance(arg,int):
                                    argvalidator = intvalidator
                                else:
                                    argvalidator = None
#                                if not isinstance(arg,np.ndarray):
                                argwidget = QLineEdit(str(arg))
                                argwidget.setValidator(argvalidator)
                                argwidget.editingFinished.connect(lambda plkeymap=dkeymap,plwidget=totalwidget,pldictkey=k:self.rebuildCommands(plkeymap,plwidget,pldictkey))
                                itemN = QListWidgetItem()
                                itemN.setSizeHint(argwidget.sizeHint())
                                commandargs.addItem(itemN)
                                commandargs.setItemWidget(itemN,argwidget)
                            commandkwargs = QListWidget()
                            for kwarg in cmd['kwargs']:
                                if isinstance(cmd['kwargs'][kwarg],float):
                                    kwargvalidator = doublevalidator
                                elif isinstance(cmd['kwargs'][kwarg],int):
                                    kwargvalidator = intvalidator
                                else:
                                    kwargvalidator = None
                                itemN = QListWidgetItem() 
                                kwarglayout = QHBoxLayout()
                                kwargname = QLabel(kwarg)
                                if kwarg in ['color','closed','fill','ls','transform']:
                                    kwargVal = QComboBox()
                                    if kwarg == 'color':
                                        kwargVal.addItems(mplcolors)
                                    elif kwarg == 'closed':
                                        kwargVal.addItems(['True','False'])
                                    elif kwarg == 'fill':
                                        kwargVal.addItems(['True','False'])
                                    elif kwarg == 'ls':
                                        kwargVal.addItems(mpllines)
                                    elif kwarg == 'transform':
                                        kwargVal.addItems(TRANSFORMS)
                                    index = kwargVal.findText(str(cmd['kwargs'][kwarg]).strip("'''"))
                                    kwargVal.setCurrentIndex(index)
                                    kwargVal.currentIndexChanged.connect(lambda trash, plkeymap=dkeymap,plwidget=totalwidget,pldictkey=k:self.rebuildCommands(plkeymap,plwidget,pldictkey))
                                else:
                                    kwargVal = QLineEdit(str(cmd['kwargs'][kwarg]))
                                    kwargVal.setValidator(kwargvalidator)
                                    kwargVal.editingFinished.connect(lambda plkeymap=dkeymap,plwidget=totalwidget,pldictkey=k:self.rebuildCommands(plkeymap,plwidget,pldictkey))
                                kwarglayout.addWidget(kwargname)
                                kwarglayout.addWidget(kwargVal)
                                kwargwidget = QWidget()
                                kwargwidget.setLayout(kwarglayout)
                                itemN.setSizeHint(kwargwidget.sizeHint()) 
                                commandkwargs.addItem(itemN)
                                commandkwargs.setItemWidget(itemN,kwargwidget)
                            toplevellayout.addWidget(commandname,1,0)
                            toplevellayout.addWidget(commandargs,1,1)
                            toplevellayout.addWidget(commandkwargs,1,2)
                            argpushbutton = QPushButton('Add Arg')
                            kwargpushbutton = QPushButton('Add Kwarg')
                            rargpushbutton = QPushButton('Remove Arg')
                            rkwargpushbutton=QPushButton('Remove Kwarg')
                            toplevellayout.addWidget(argpushbutton,2,1)
                            toplevellayout.addWidget(kwargpushbutton,2,2)
                            toplevellayout.addWidget(rargpushbutton,3,1)
                            toplevellayout.addWidget(rkwargpushbutton,3,2)
                            rargpushbutton.clicked.connect(lambda trash,listwidget=commandargs:self.removeArg(listwidget))
                            rkwargpushbutton.clicked.connect(lambda trash,listwidget=commandkwargs:self.removeKwarg(listwidget))
                            argpushbutton.clicked.connect(lambda trash,listwidget=commandargs,plwidget=totalwidget,plkeymap=dkeymap,pldictkey=k:self.addArg(listwidget,plwidget,plkeymap,pldictkey))
                            kwargpushbutton.clicked.connect(lambda trash, listwidget=commandkwargs,plwidget=totalwidget,plkeymap=dkeymap,pldictkey=k:self.addKwarg(listwidget,plwidget,plkeymap,pldictkey))
                            nwidget.setLayout(toplevellayout)
                            totallayout.addWidget(nwidget)
                    grandchild = QTreeWidgetItem(child)
                    totalwidget.setLayout(totallayout)
                    self.nestedwidgets[key][k].append(totalwidget)
                    self.currentTreeWidget.setItemWidget(grandchild,0,self.nestedwidgets[key][k][-1])
                    grandchild = QTreeWidgetItem(child)
                    addcommand = QPushButton('Add Command')
                    removecommand = QPushButton('Remove Command')
                    self.currentTreeWidget.setItemWidget(grandchild,0,addcommand)
                    grandchild = QTreeWidgetItem(child)
                    self.currentTreeWidget.setItemWidget(grandchild,0,removecommand)
                    addcommand.clicked.connect(lambda trash, plkeymap = dkeymap,plkey=k,pllayout=self.nestedwidgets[key][k][-1].layout(),plwidget=totalwidget:self.addCommand(plkeymap,plkey,pllayout,plwidget))
                    removecommand.clicked.connect(lambda trash, plkeymap = dkeymap,plkey=k,pllayout=self.nestedwidgets[key][k][-1].layout(),plwidget=totalwidget:self.removeCommand(plkeymap,plkey,pllayout,plwidget))
                elif k in ['patches']:
                    self.nestedwidgets[key][k]=[]
                    ptotallayout = QVBoxLayout()
                    ptotalwidget = QWidget()
                    if d[k]:
                        #cmd is list of commands
                        for pcmd in d[k]:
                            ptoplevellayout = QGridLayout()
                            ptoplevellayout.addWidget(QLabel('Patch Type'),0,0)
                            ptoplevellayout.addWidget(QLabel('Args'),0,1)
                            ptoplevellayout.addWidget(QLabel('Kwargs'),0,2)
                            pnwidget = QWidget()
                            pcommandname = QLineEdit(pcmd['cmd'])
                            pcommandname.setValidator(None)
                            pcommandname.setReadOnly(True)
                            pcommandargs = QListWidget()
                            pcommandname.editingFinished.connect(lambda plkeymap=dkeymap,plwidget=ptotalwidget,pldictkey=k:self.rebuildCommands(plkeymap,plwidget,pldictkey))
                            for parg in pcmd['args']:
                                if isinstance(parg,float):
                                    pargvalidator = doublevalidator
                                elif isinstance(parg,int):
                                    pargvalidator = intvalidator
                                else:
                                    pargvalidator = None
#                                if not isinstance(arg,np.ndarray):
                                pargwidget = QLineEdit(str(parg))
                                pargwidget.setValidator(pargvalidator)
#                                argwidget.setReadOnly(True)
                                pargwidget.editingFinished.connect(lambda plkeymap=dkeymap,plwidget=ptotalwidget,pldictkey=k:self.rebuildCommands(plkeymap,plwidget,pldictkey))
                                pitemN = QListWidgetItem()
                                pitemN.setSizeHint(argwidget.sizeHint())
                                pcommandargs.addItem(pitemN)
                                pcommandargs.setItemWidget(pitemN,pargwidget)
                            pcommandkwargs = QListWidget()
                            for ii,pkwarg in enumerate(pcmd['kwargs']):
                                if isinstance(pcmd['kwargs'][pkwarg],float):
                                    pkwargvalidator = doublevalidator
                                elif isinstance(pcmd['kwargs'][pkwarg],int):
                                    pkwargvalidator = intvalidator
                                else:
                                    pkwargvalidator = None
                                pitemN = QListWidgetItem() 
                                pkwarglayout = QHBoxLayout()
                                pkwargname = QLabel(pkwarg)
                                if pkwarg in ['color','closed','fill','ls','transform']:
                                    pkwargVal = QComboBox()
                                    if pkwarg == 'color':
                                        pkwargVal.addItems(mplcolors)
                                    elif pkwarg == 'closed':
                                        pkwargVal.addItems(['True','False'])
                                    elif pkwarg == 'fill':
                                        pkwargVal.addItems(['True','False'])
                                    elif pkwarg == 'ls':
                                        pkwargVal.addItems(mpllines)
                                    elif pkwarg == 'transform':
                                        pkwargVal.addItems(TRANSFORMS)
                                    index = pkwargVal.findText(str(pcmd['kwargs'][pkwarg]).strip("'''"))
                                    pkwargVal.setCurrentIndex(index)
                                    pkwargVal.currentIndexChanged.connect(lambda trash, plkeymap=dkeymap,plwidget=ptotalwidget,pldictkey=k:self.rebuildCommands(plkeymap,plwidget,pldictkey))
                                else:
                                    pkwargVal = QLineEdit(str(pcmd['kwargs'][pkwarg]))
                                    pkwargVal.setValidator(pkwargvalidator)
                                    pkwargVal.editingFinished.connect(lambda plkeymap=dkeymap,plwidget=ptotalwidget,pldictkey=k:self.rebuildCommands(plkeymap,plwidget,pldictkey))
                                pkwarglayout.addWidget(pkwargname)
                                pkwarglayout.addWidget(pkwargVal)
                                pkwargwidget = QWidget()
                                pkwargwidget.setLayout(pkwarglayout)
                                pitemN.setSizeHint(pkwargwidget.sizeHint()) 
                                pcommandkwargs.addItem(pitemN)
                                pcommandkwargs.setItemWidget(pitemN,pkwargwidget)
                            ptoplevellayout.addWidget(pcommandname,1,0)
                            ptoplevellayout.addWidget(pcommandargs,1,1)
                            ptoplevellayout.addWidget(pcommandkwargs,1,2)
                            pargpushbutton = QPushButton('Add Arg')
                            pkwargpushbutton = QPushButton('Add Kwarg')
                            prargpushbutton = QPushButton('Remove Arg')
                            prkwargpushbutton=QPushButton('Remove Kwarg')
                            ptoplevellayout.addWidget(pargpushbutton,2,1)
                            ptoplevellayout.addWidget(pkwargpushbutton,2,2)
                            ptoplevellayout.addWidget(prargpushbutton,3,1)
                            ptoplevellayout.addWidget(prkwargpushbutton,3,2)
                            prargpushbutton.clicked.connect(lambda trash,listwidget=pcommandargs:self.removeArg(listwidget))
                            prkwargpushbutton.clicked.connect(lambda trash,listwidget=pcommandkwargs:self.removeKwarg(listwidget))
                            pargpushbutton.clicked.connect(lambda trash,listwidget=pcommandargs,plwidget=ptotalwidget,plkeymap=dkeymap,pldictkey=k:self.addArg(listwidget,plwidget,plkeymap,pldictkey))
                            pkwargpushbutton.clicked.connect(lambda trash, listwidget=pcommandkwargs,plwidget=ptotalwidget,plkeymap=dkeymap,pldictkey=k:self.addKwarg(listwidget,plwidget,plkeymap,pldictkey))
                            pnwidget.setLayout(ptoplevellayout)
                            ptotallayout.addWidget(pnwidget)
                    grandchild = QTreeWidgetItem(child)
                    ptotalwidget.setLayout(ptotallayout)
                    self.nestedwidgets[key][k].append(ptotalwidget)
                    self.currentTreeWidget.setItemWidget(grandchild,0,self.nestedwidgets[key][k][-1])
                    grandchild = QTreeWidgetItem(child)
                    paddcommand = QPushButton('Add Patch')
                    premovecommand = QPushButton('Remove Patch')
                    self.currentTreeWidget.setItemWidget(grandchild,0,paddcommand)
                    grandchild = QTreeWidgetItem(child)
                    self.currentTreeWidget.setItemWidget(grandchild,0,premovecommand)
                    paddcommand.clicked.connect(lambda trash, plkeymap = dkeymap,plkey=k,pllayout=self.nestedwidgets[key][k][-1].layout(),plwidget=ptotalwidget:self.addPatch(plkeymap,plkey,pllayout,plwidget))
                    premovecommand.clicked.connect(lambda trash, plkeymap = dkeymap,plkey=k,pllayout=self.nestedwidgets[key][k][-1].layout(),plwidget=ptotalwidget:self.removeCommand(plkeymap,plkey,pllayout,plwidget))
                #Line edit for single values
                elif isinstance(v, str):
                    if v:
                        self.nestedwidgets[key][k] = QLineEdit(v)
                        self.nestedwidgets[key][k].setValidator(validator)
                        grandchild = QTreeWidgetItem(child)
                        self.currentTreeWidget.setItemWidget(grandchild,0,self.nestedwidgets[key][k])
                        self.nestedwidgets[key][k].editingFinished.connect(lambda plwidget=self.nestedwidgets[key][k],plkey=key,pldictkey=k,plkeymap=dkeymap,vtype = ogtype:self.updateDict(plwidget,plkey,pldictkey,plkeymap,vtype))
                    else:
                        self.parent.removeChild(child)
                elif isinstance(v,list):
                    if len(v) and isinstance(v[0],dict):
                        for i in range(len(v)):
                            nkeymap=copy.copy(dkeymap)
                            nkeymap.append(unalteredk)
                            nkeymap.append(i)
                            grandchild = QTreeWidgetItem(child)
                            grandchild.setText(0,str(i))
                            v[i] = walkDict(v[i],grandchild,nkeymap)
                        continue
                    self.nestedwidgets[key][k] = []
                    if len(v):
                        for item in v:
                            self.nestedwidgets[key][k].append(QLineEdit(str(v)))
                            self.nestedwidgets[key][k][-1].setValidator(validator)
                            grandchild = QTreeWidgetItem(child)
                            self.currentTreeWidget.setItemWidget(grandchild,0,self.nestedwidgets[key][k][-1])
                            self.nestedwidgets[key][k][-1].editingFinished.connect(lambda plwidget=self.nestedwidgets[key][k][-1],plkey=key,pldictkey=k,plkeymap=dkeymap,vtype=ogtype:self.updateDict(plwidget,plkey,pldictkey,plkeymap,vtype))
                    else:
                        self.parent.removeChild(child)
                else:
                    self.nestedwidgets[key][k] = QLineEdit(str(v))
                    self.nestedwidgets[key][k].setValidator(validator)
                    grandchild = QTreeWidgetItem(child)
                    self.currentTreeWidget.setItemWidget(grandchild,0,self.nestedwidgets[key][k])
                    self.nestedwidgets[key][k].editingFinished.connect(lambda plwidget=self.nestedwidgets[key][k],plkey=key,pldictkey=k,plkeymap=dkeymap,vtype=ogtype:self.updateDict(plwidget,plkey,pldictkey,plkeymap,vtype))
        for i,key in enumerate(treedata):
            if key not in noshow_keys:
#                parent = QTreeWidgetItem(widget)
#                parent.setText(0,key)
#                parent.setFlags(parent.flags())
                parent = None
                keymap = [key]
                if isinstance(treedata[key],dict):
                    walkDict(treedata[key],parent,keymap)
                elif isinstance(treedata[key],list):
                    if isinstance(treedata[key],dict):
                        walkDict(dict(Placeholder=treedata[key]),parent,keymap)
        self.currentTreeWidget.expandAll()
    
    def removeArg(self,widget):
        for SelectedItem in widget.selectedItems():
            widget.takeItem(widget.row(SelectedItem))
    
    def removeKwarg(self,widget):
        for SelectedItem in widget.selectedItems():
            widget.takeItem(widget.row(SelectedItem))
    
    def addArg(self,widget,totalwidget,dkeymap,key):
        itemN = QListWidgetItem()
        le = QLineEdit()
        itemN.setSizeHint(le.sizeHint())
        widget.addItem(itemN)
        widget.setItemWidget(itemN,le)
        le.editingFinished.connect(lambda plkeymap=dkeymap,plwidget=totalwidget,plkey=key:self.rebuildCommands(plkeymap,plwidget,plkey))
        
    def addKwarg(self,widget,totalwidget,dkeymap,key,labelName=None,value=None):
        itemN = QListWidgetItem()
        if not labelName:
            labelName = getlabel()
        if labelName in ['color','closed','fill','ls','transform']:
            kwargVal = QComboBox()
            if labelName == 'color':
                kwargVal.addItems(mplcolors)
            elif labelName == 'closed':
                kwargVal.addItems(['True','False'])
            elif labelName == 'fill':
                kwargVal.addItems(['True','False'])
            elif labelName == 'ls':
                kwargVal.addItems(mpllines)
            elif labelName == 'transform':
                kwargVal.addItems(TRANSFORMS)
            if value:
                index = kwargVal.findText(value)
                kwargVal.setCurrentIndex(index)
            else:
                kwargVal.setCurrentIndex(0)
            kwargVal.currentIndexChanged.connect(lambda trash, plkeymap=dkeymap,plwidget=totalwidget,pldictkey=key:self.rebuildCommands(plkeymap,plwidget,pldictkey))
        else:
            if not value:
                kwargVal = QLineEdit()
            else:
                kwargVal = QLineEdit(value)
            kwargVal.editingFinished.connect(lambda plkeymap=dkeymap,plwidget=totalwidget,plkey=key:self.rebuildCommands(plkeymap,plwidget,plkey))
        label = QLabel(labelName)
        layout = QHBoxLayout()
        container = QWidget()
        layout.addWidget(label)
        layout.addWidget(kwargVal)
        container.setLayout(layout)
        itemN.setSizeHint(container.sizeHint())
        widget.addItem(itemN)
        widget.setItemWidget(itemN,container)
        
        
    def addCommand(self,keymap,key,layout,totalwidget):
        toplevellayout = QGridLayout()
        toplevellayout.addWidget(QLabel('Command'),0,0)
        toplevellayout.addWidget(QLabel('Args'),0,1)
        toplevellayout.addWidget(QLabel('Kwargs'),0,2)
        nwidget = QWidget()
        commandname = QLineEdit()
        commandname.editingFinished.connect(lambda plkeymap=keymap,plwidget=totalwidget,plkey=key:self.rebuildCommands(plkeymap,plwidget,plkey))
        commandargs = QListWidget()
        commandkwargs = QListWidget()
        toplevellayout.addWidget(commandname,1,0)
        toplevellayout.addWidget(commandargs,1,1)
        toplevellayout.addWidget(commandkwargs,1,2)
        argpushbutton = QPushButton('Add Arg')
        kwargpushbutton = QPushButton('Add Kwarg')
        rargpushbutton = QPushButton('Remove Arg')
        rkwargpushbutton=QPushButton('Remove Kwarg')
        toplevellayout.addWidget(argpushbutton,2,1)
        toplevellayout.addWidget(kwargpushbutton,2,2)
        toplevellayout.addWidget(rargpushbutton,3,1)
        toplevellayout.addWidget(rkwargpushbutton,3,2)
        rargpushbutton.clicked.connect(lambda trash,listwidget=commandargs:self.removeArg(listwidget))
        rkwargpushbutton.clicked.connect(lambda trash,listwidget=commandkwargs:self.removeKwarg(listwidget))
        argpushbutton.clicked.connect(lambda trash,listwidget=commandargs,plwidget=totalwidget,plkeymap=keymap,pldictkey=key:self.addArg(listwidget,plwidget,plkeymap,pldictkey))
        kwargpushbutton.clicked.connect(lambda trash, listwidget=commandkwargs,plwidget=totalwidget,plkeymap=keymap,pldictkey=key:self.addKwarg(listwidget,plwidget,plkeymap,pldictkey))
        nwidget.setLayout(toplevellayout)
        layout.addWidget(nwidget)
    
    def addPatch(self,keymap,key,layout,totalwidget):
        patchtype = getSelectedItems(mplpatches)
        toplevellayout = QGridLayout()
        toplevellayout.addWidget(QLabel('Patch Type'),0,0)
        toplevellayout.addWidget(QLabel('Args'),0,1)
        toplevellayout.addWidget(QLabel('Kwargs'),0,2)
        nwidget = QWidget()
        commandname = QComboBox()
        commandname.addItems(mplpatches)
        index = commandname.findText(patchtype)
        commandname.setCurrentIndex(index)
        commandargs = QListWidget()
        commandkwargs = QListWidget()
        commandname.currentIndexChanged.connect(lambda trash, plkey=key,plkeymap=keymap,plcombo=commandname,pltotwidget=totalwidget,plarglist=commandargs,plkwarglist=commandkwargs:self.changePatch(plkey,plkeymap,plcombo,plarglist,plkwarglist,pltotwidget))
        
        if patchtype in ['Rectangle','Ellipse']:
            self.addKwarg(commandkwargs,totalwidget,keymap,key,'xy','(0.0,0.0)')
            self.addKwarg(commandkwargs,totalwidget,keymap,key,'width','1.0')
            self.addKwarg(commandkwargs,totalwidget,keymap,key,'height','1.0')
            self.addKwarg(commandkwargs,totalwidget,keymap,key,'angle','0.0')
        elif patchtype == 'Circle':
            self.addKwarg(commandkwargs,totalwidget,keymap,key,'xy','(0.0,0.0)')
            self.addKwarg(commandkwargs,totalwidget,keymap,key,'radius','1.0')
        elif patchtype == 'Polygon':
            self.addKwarg(commandkwargs,totalwidget,keymap,key,'xy','(0.0,0.0)')
            self.addKwarg(commandkwargs,totalwidget,keymap,key,'closed')
        self.addKwarg(commandkwargs,totalwidget,keymap,key,'fill','True')
        self.addKwarg(commandkwargs,totalwidget,keymap,key,'alpha','1.0')
        self.addKwarg(commandkwargs,totalwidget,keymap,key,'color','black')
        self.addKwarg(commandkwargs,totalwidget,keymap,key,'ls','--')
        self.addKwarg(commandkwargs,totalwidget,keymap,key,'zorder','1')
            
        
        toplevellayout.addWidget(commandname,1,0)
        toplevellayout.addWidget(commandargs,1,1)
        toplevellayout.addWidget(commandkwargs,1,2)
        argpushbutton = QPushButton('Add Arg')
        kwargpushbutton = QPushButton('Add Kwarg')
        rargpushbutton = QPushButton('Remove Arg')
        rkwargpushbutton=QPushButton('Remove Kwarg')
        toplevellayout.addWidget(argpushbutton,2,1)
        toplevellayout.addWidget(kwargpushbutton,2,2)
        toplevellayout.addWidget(rargpushbutton,3,1)
        toplevellayout.addWidget(rkwargpushbutton,3,2)
        rargpushbutton.clicked.connect(lambda trash,listwidget=commandargs:self.removeArg(listwidget))
        rkwargpushbutton.clicked.connect(lambda trash,listwidget=commandkwargs:self.removeKwarg(listwidget))
        argpushbutton.clicked.connect(lambda trash,listwidget=commandargs,plwidget=totalwidget,plkeymap=keymap,pldictkey=key:self.addArg(listwidget,plwidget,plkeymap,pldictkey))
        kwargpushbutton.clicked.connect(lambda trash, listwidget=commandkwargs,plwidget=totalwidget,plkeymap=keymap,pldictkey=key:self.addKwarg(listwidget,plwidget,plkeymap,pldictkey))
        nwidget.setLayout(toplevellayout)
        layout.addWidget(nwidget)
        self.rebuildCommands(keymap,totalwidget,key)
        
    def changePatch(self,key,keymap,patchcombo,arglist,kwarglist,totalwidget):
        arglist.clear()
        kwarglist.clear()
        patchtype = patchcombo.currentText()
        if patchtype in ['Rectangle','Ellipse']:
            self.addKwarg(kwarglist,totalwidget,keymap,key,'xy','(0.0,0.0)')
            self.addKwarg(kwarglist,totalwidget,keymap,key,'width','1.0')
            self.addKwarg(kwarglist,totalwidget,keymap,key,'height','1.0')
            self.addKwarg(kwarglist,totalwidget,keymap,key,'angle','0.0')
        elif patchtype == 'Circle':
            self.addKwarg(kwarglist,totalwidget,keymap,key,'xy','(0.0,0.0)')
            self.addKwarg(kwarglist,totalwidget,keymap,key,'radius','1.0')
        elif patchtype == 'Polygon':
            self.addKwarg(kwarglist,totalwidget,keymap,key,'xy','(0.0,0.0)')
            self.addKwarg(kwarglist,totalwidget,keymap,key,'closed')
        self.addKwarg(kwarglist,totalwidget,keymap,key,'fill','True')
        self.addKwarg(kwarglist,totalwidget,keymap,key,'alpha','1.0')
        self.addKwarg(kwarglist,totalwidget,keymap,key,'color','black')
        self.addKwarg(kwarglist,totalwidget,keymap,key,'ls','-')
        self.addKwarg(kwarglist,totalwidget,keymap,key,'zorder','1')
        self.rebuildCommands(keymap,totalwidget,key)
        
    def removeCommand(self,keymap,key,layout,totalwidget):
        listofcommands = []
        for i in range(layout.count()):
            thewidget = layout.itemAt(i).widget().layout().itemAt(3).widget()
            if isinstance(thewidget,QLineEdit):
                listofcommands.append(thewidget.text())
            elif isinstance(thewidget,QComboBox):
                listofcommands.append(thewidget.currentText())
        selected = getSelectedItems(listofcommands)
        if selected:
            index = listofcommands.index(selected)
            layout.itemAt(index).widget().deleteLater()
            layout.itemAt(index).widget().setParent(None)
        self.rebuildCommands(keymap,totalwidget,key)
        
        
    def updateDict(self,widget,key,dictkey,keymap,vtype):
        if isinstance(widget,QLineEdit):
            text = widget.text()
        elif isinstance(widget,QComboBox):
            text = widget.currentText()
        self.getFromDict(keymap)[dictkey] = vtype(text)
        self.preview()
        
    def handleList(self,widget,dictkey,keymap,index,vtype):
        if isinstance(widget,QComboBox):
            txt = widget.currentText()
        else:
            txt = widget.text()
        self.getFromDict(keymap)[dictkey][index]=vtype(txt)
        self.preview()
            
    def getFromDict(self,maplist):
        return reduce(operator.getitem,maplist,self.plotDict)
    
    def rebuildCommands(self,keymap,widget,plkey):
        commands = []
        for i in range(widget.layout().count()):
            contents = {}
            underlying = widget.layout().itemAt(i).widget().layout()
            commandle = underlying.itemAt(3).widget()
            arglw = underlying.itemAt(4).widget()
            kwarglw = underlying.itemAt(5).widget()
            if isinstance(commandle,QLineEdit):
                command = commandle.text()
            elif isinstance(commandle,QComboBox):
                command = commandle.currentText()
            else:
                command = None
            if command:
                args = []
                kwargs = {}
                for j in range(arglw.count()):
                    arg = arglw.itemWidget(arglw.item(j)).text()
                    try:
                        arg = eval(arg)
                    except:
                        if arg.startswith('['):
                            self.Alert('Assuming '+'"'+str(arg)+'"'+' is a numpy array')
                            arg = re.sub(r'\n',' ',arg)
                            arg = re.sub(r' +',' ',arg)
                            arg = re.sub(r'\[ +',r'[',arg)
                            arg = re.sub(r' +\]',r']',arg)
                            for bracketed in re.findall(r"\[(.+?)\]",arg):
                                arg = arg.replace(bracketed,bracketed.replace(" ",","))
                            arg = arg.replace('] [','],[')
                            arg = arg.replace(' ','')
                            arg = np.array(eval(arg))
                        else:
                            self.Alert('Assuming '+'"'+str(arg)+'"'+' is a string.')
                            arg = str(arg)
                    if isinstance(arg,str):
                        arg = "'''{}'''".format(arg)
                    args.append(arg)
                for j in range(kwarglw.count()):
                    key = kwarglw.itemWidget(kwarglw.item(j)).layout().itemAt(0).widget().text()
                    if isinstance(kwarglw.itemWidget(kwarglw.item(j)).layout().itemAt(1).widget(),QLineEdit):
                        kwarg = kwarglw.itemWidget(kwarglw.item(j)).layout().itemAt(1).widget().text()
                    elif isinstance(kwarglw.itemWidget(kwarglw.item(j)).layout().itemAt(1).widget(),QComboBox):
                        kwarg = kwarglw.itemWidget(kwarglw.item(j)).layout().itemAt(1).widget().currentText()
                    try:
                        kwarg = eval(kwarg)
                    except:
                        if kwarg.startswith('['):
                            self.Alert('Assuming '+'"'+str(kwarg)+'"'+' is a numpy array')
                            kwarg = re.sub(r'\n',' ',kwarg)
                            kwarg = re.sub(r' +',' ',kwarg)
                            kwarg = re.sub(r'\[ +',r'[',kwarg)
                            kwarg = re.sub(r' +\]',r']',kwarg)
                            for bracketed in re.findall(r"\[(.+?)\]",kwarg):
                                kwarg = kwarg.replace(bracketed,bracketed.replace(" ",","))
                            kwarg = kwarg.replace('] [','],[')
                            kwarg = kwarg.replace(' ','')
                            kwarg = np.array(eval(kwarg))
                        else:
                            self.Alert('Assuming '+'"'+str(kwarg)+'"'+' is a string.')
                            kwarg = str(kwarg)
                    if isinstance(kwarg,str):
                        kwarg = "'''{}'''".format(kwarg)
                    kwargs[key]=kwarg
                contents['cmd'] = command
                contents['args'] = args
                contents['kwargs'] = kwargs
                commands.append(contents)
        self.getFromDict(keymap)[plkey] = commands
        self.preview()

def main():
    app = QApplication(sys.argv)
    frame = Pleditor()
    frame.show()
    retval = app.exec_()
    sys.exit(retval)


if __name__ == '__main__':
    main()