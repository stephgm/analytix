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
from matplotlib.backends.backend_qt5agg import (FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
colors = dict(matplotlib.colors.BASE_COLORS, **matplotlib.colors.CSS4_COLORS)
by_hsv = sorted((tuple(matplotlib.colors.rgb_to_hsv(matplotlib.colors.to_rgba(color)[:3])), name)
                for name, color in colors.items())
mplcolors = [name for hsv, name in by_hsv]
mplsymbols = filter(lambda i:(((type(i) is unicode) or (type(i) is str)) and (i != 'None') and i),matplotlib.markers.MarkerStyle.markers.keys())
mplcmaps = sorted(m for m in matplotlib.pyplot.cm.datad if not m.endswith("_r"))
mpllines = matplotlib.lines.lineStyles.keys()
TRANSFORMS = ['PlateCarree()','NorthPolarStereo()','EckertV()','RotatedPole()','Orthographic()']

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
    return widget.listwidget.currentItem().text()

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
        fname = r'C:\Users\Jordan\Phobos_Plots\06-29-2019_10_55_55.pklplt'
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
            print 'ha'
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
            self.plotDict = cPickle.load(file(self.fname,'rb'))
            self.setupTreeWidget(self.PlotOptionsTree,self.plotDict)
            self.preview()
            
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
                myfig = pltr.createPlot('',RETURN=True)
                self.CanvasLayout.addWidget(self.dynamic_canvas)
                self.dynamic_canvas.figure = myfig
                self.isValid = True
        except:
            self.dynamic_canvas = FigureCanvas(matplotlib.figure.Figure())
            self.dynamic_canvas.figure = old
            self.CanvasLayout.addWidget(self.dynamic_canvas)
            self.isValid = False
            self.Alert('Maybe a kwarg needs to be updated')
    
    def save(self,override=False):
        if self.fname and (self.isValid or override):
            pltr = plrt.Plotter()
            pltr.sub = self.plotDict['sub']
            pltr.fig = self.plotDict['fig']
            if override:
                pltr.savePkl(self.fname+'_INVALID.pklplt')
            else:
                pltr.createPlot(self.fname+'_Edited.pklplt',SAVE=True,SAVEPKL=True)
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
        plottype = treedata['sub']
        self.PlotOptionsTree.clear()
        widget.blockSignals(True)
        self.nestedwidgets = {key:{} for key in treedata.keys()}
        def walkDict(d,parent,dkeymap):
            key = dkeymap[0]
            d = OrderedDict(d)
            for k, v in d.iteritems():
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
                    child = QTreeWidgetItem(parent)
                    child.setText(0,k)
                else:
                    child = QTreeWidgetItem(parent)
                    child.setText(0,k)
                if isinstance(v, dict) and k not in ['commands']:
                    child.setFlags(child.flags())
                    nkeymap = copy.copy(dkeymap)
                    nkeymap.append(unalteredk)
                    if v:
                        v = walkDict(v,child,nkeymap)
                    else:
                        parent.removeChild(child)
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
                    widget.setItemWidget(grandchild,0,self.nestedwidgets[key][k])
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
                    widget.setItemWidget(grandchild,0,self.nestedwidgets[key][k])
                elif k in ['cmap','picker','marker','mapproj','transform','ls','linestyle']:
                    if isinstance(d[k],np.ndarray) or isinstance(d[k],pd.DataFrame) or isinstance(d[k],pd.Series):
                        parent.removeChild(child)
                        continue
                    if not d[k]:
                        parent.removeChild(child)
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
                    widget.setItemWidget(grandchild,0,self.nestedwidgets[key][k])
                    self.nestedwidgets[key][k].currentIndexChanged.connect(lambda trash, plwidget=self.nestedwidgets[key][k],plkey=key,pldictkey=k,plkeymap=dkeymap,vtype=ogtype:self.updateDict(plwidget,plkey,pldictkey,plkeymap,vtype))
                elif k in ['c','colors','color']:
                    if isinstance(d[k],np.ndarray) or isinstance(d[k],pd.DataFrame) or isinstance(d[k],pd.Series):
                        parent.removeChild(child)
                        continue
                    if not d[k]:
                        parent.removeChild(child)
                        continue
                    self.nestedwidgets[key][k] = []
                    if isinstance(v,list):
                        for i,item in enumerate(v):
                            self.nestedwidgets[key][k].append(QComboBox())
                            grandchild = QTreeWidgetItem(child)
                            self.nestedwidgets[key][k][-1].addItems(mplcolors)
                            index = self.nestedwidgets[key][k][-1].findText(str(item))
                            self.nestedwidgets[key][k][-1].setCurrentIndex(index)
                            widget.setItemWidget(grandchild,0,self.nestedwidgets[key][k][-1])
                            self.nestedwidgets[key][k][-1].currentIndexChanged.connect(lambda trash,plwidget=self.nestedwidgets[key][k][-1],pldictkey=k,plkeymap=dkeymap,index=i,vtype=str:self.handleList(plwidget,pldictkey,plkeymap,index,vtype))
                    else:
                        self.nestedwidgets[key][k] = QComboBox()
                        grandchild = QTreeWidgetItem(child)
                        self.nestedwidgets[key][k].addItems(mplcolors)
                        index = self.nestedwidgets[key][k].findText(str(v))
                        self.nestedwidgets[key][k].setCurrentIndex(index)
                        widget.setItemWidget(grandchild,0,self.nestedwidgets[key][k])
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
                        widget.setItemWidget(grandchild,0,self.nestedwidgets[key][k][-1])
                        j+=1
                elif k in ['rowspan','colspan','zorder','s']:
                    le = QLineEdit(str(v))
                    le.setValidator(validator)
                    le.textChanged.connect(lambda trash, plwidget=le,plkey=key,pldictkey=k,plkeymap=dkeymap,vtype=ogtype:self.updateDict(plwidget,plkey,pldictkey,plkeymap,vtype))
                    self.nestedwidgets[key][k] = le
                    grandchild = QTreeWidgetItem(child)
                    widget.setItemWidget(grandchild,0,self.nestedwidgets[key][k])
                elif k in ['table']:
                    parent.removeChild(child)
                    continue
                elif k in ['commands','patches']:
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
                            commandname.editingFinished.connect(lambda plkeymap=dkeymap,plwidget=totalwidget:self.rebuildCommands(plkeymap,plwidget))
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
                                argwidget.editingFinished.connect(lambda plkeymap=dkeymap,plwidget=totalwidget:self.rebuildCommands(plkeymap,plwidget))
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
                                kwargVal = QLineEdit(str(cmd['kwargs'][kwarg]))
                                kwargVal.setValidator(kwargvalidator)
                                kwargVal.editingFinished.connect(lambda plkeymap=dkeymap,plwidget=totalwidget:self.rebuildCommands(plkeymap,plwidget))
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
                            argpushbutton.clicked.connect(lambda trash,listwidget=commandargs,plwidget=totalwidget,plkeymap=dkeymap:self.addArg(listwidget,plwidget,plkeymap))
                            kwargpushbutton.clicked.connect(lambda trash, listwidget=commandkwargs,plwidget=totalwidget,plkeymap=dkeymap:self.addKwarg(listwidget,plwidget,plkeymap))
                            nwidget.setLayout(toplevellayout)
                            totallayout.addWidget(nwidget)
                    grandchild = QTreeWidgetItem(child)
                    totalwidget.setLayout(totallayout)
                    self.nestedwidgets[key][k].append(totalwidget)
                    widget.setItemWidget(grandchild,0,self.nestedwidgets[key][k][-1])
                    grandchild = QTreeWidgetItem(child)
                    addcommand = QPushButton('Add Command')
                    removecommand = QPushButton('Remove Command')
                    widget.setItemWidget(grandchild,0,addcommand)
                    grandchild = QTreeWidgetItem(child)
                    widget.setItemWidget(grandchild,0,removecommand)
                    addcommand.clicked.connect(lambda trash, plkeymap = dkeymap,plkey=k,pllayout=self.nestedwidgets[key][k][-1].layout(),plwidget=totalwidget:self.addCommand(plkeymap,plkey,pllayout,plwidget))
                    removecommand.clicked.connect(lambda trash, plkeymap = dkeymap,plkey=k,pllayout=self.nestedwidgets[key][k][-1].layout():self.removeCommand(plkeymap,plkey,pllayout))
                #Line edit for single values
                elif isinstance(v, str):
                    if v:
                        self.nestedwidgets[key][k] = QLineEdit(v)
                        self.nestedwidgets[key][k].setValidator(validator)
                        grandchild = QTreeWidgetItem(child)
                        widget.setItemWidget(grandchild,0,self.nestedwidgets[key][k])
                        self.nestedwidgets[key][k].editingFinished.connect(lambda plwidget=self.nestedwidgets[key][k],plkey=key,pldictkey=k,plkeymap=dkeymap,vtype = ogtype:self.updateDict(plwidget,plkey,pldictkey,plkeymap,vtype))
                    else:
                        parent.removeChild(child)
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
                            widget.setItemWidget(grandchild,0,self.nestedwidgets[key][k][-1])
                            self.nestedwidgets[key][k][-1].editingFinished.connect(lambda plwidget=self.nestedwidgets[key][k][-1],plkey=key,pldictkey=k,plkeymap=dkeymap,vtype=ogtype:self.updateDict(plwidget,plkey,pldictkey,plkeymap,vtype))
                    else:
                        parent.removeChild(child)
                else:
                    self.nestedwidgets[key][k] = QLineEdit(str(v))
                    self.nestedwidgets[key][k].setValidator(validator)
                    grandchild = QTreeWidgetItem(child)
                    widget.setItemWidget(grandchild,0,self.nestedwidgets[key][k])
                    self.nestedwidgets[key][k].editingFinished.connect(lambda plwidget=self.nestedwidgets[key][k],plkey=key,pldictkey=k,plkeymap=dkeymap,vtype=ogtype:self.updateDict(plwidget,plkey,pldictkey,plkeymap,vtype))
        for i,key in enumerate(treedata):
            if key not in noshow_keys:
                parent = QTreeWidgetItem(widget)
                parent.setText(0,key)
                parent.setFlags(parent.flags())
                keymap = [key]
                if isinstance(treedata[key],dict):
                    walkDict(treedata[key],parent,keymap)
                elif isinstance(treedata[key],list):
                    if isinstance(treedata[key],dict):
                        walkDict(dict(Placeholder=treedata[key]),parent,keymap)
        widget.expandAll()
        widget.blockSignals(False)
    
    def removeArg(self,widget):
        for SelectedItem in widget.selectedItems():
            widget.takeItem(widget.row(SelectedItem))
    
    def removeKwarg(self,widget):
        for SelectedItem in widget.selectedItems():
            widget.takeItem(widget.row(SelectedItem))
    
    def addArg(self,widget,totalwidget,dkeymap):
        itemN = QListWidgetItem()
        le = QLineEdit()
        itemN.setSizeHint(le.sizeHint())
        widget.addItem(itemN)
        widget.setItemWidget(itemN,le)
        le.editingFinished.connect(lambda plkeymap=dkeymap,plwidget=totalwidget:self.rebuildCommands(plkeymap,totalwidget))
        
    def addKwarg(self,widget,totalwidget,dkeymap):
        itemN = QListWidgetItem()
        labelName = getlabel()
        le = QLineEdit()
        label = QLabel(labelName)
        layout = QHBoxLayout()
        container = QWidget()
        layout.addWidget(label)
        layout.addWidget(le)
        container.setLayout(layout)
        itemN.setSizeHint(container.sizeHint())
        widget.addItem(itemN)
        widget.setItemWidget(itemN,container)
        le.editingFinished.connect(lambda plkeymap=dkeymap,plwidget=totalwidget:self.rebuildCommands(plkeymap,totalwidget))
        
    def addCommand(self,keymap,key,layout,totalwidget):
        toplevellayout = QGridLayout()
        toplevellayout.addWidget(QLabel('Command'),0,0)
        toplevellayout.addWidget(QLabel('Args'),0,1)
        toplevellayout.addWidget(QLabel('Kwargs'),0,2)
        nwidget = QWidget()
        commandname = QLineEdit()
        commandname.editingFinished.connect(lambda plkeymap=keymap,plwidget=totalwidget:self.rebuildCommands(plkeymap,totalwidget))
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
        argpushbutton.clicked.connect(lambda trash,listwidget=commandargs,plwidget=totalwidget,plkeymap=keymap:self.addArg(listwidget,plwidget,plkeymap))
        kwargpushbutton.clicked.connect(lambda trash, listwidget=commandkwargs,plwidget=totalwidget,plkeymap=keymap:self.addKwarg(listwidget,plwidget,plkeymap))
        nwidget.setLayout(toplevellayout)
        layout.addWidget(nwidget)
        
    def removeCommand(self,keymap,key,layout):
        listofcommands = []
        
        for i in range(layout.count()):
            listofcommands.append(layout.itemAt(i).widget().layout().itemAt(3).widget().text())
        selected = getSelectedItems(listofcommands)
        if selected:
            index = listofcommands.index(selected)
            layout.itemAt(index).widget().deleteLater()
        
        
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
    
    def rebuildCommands(self,keymap,widget):
        commands = []
        for i in range(widget.layout().count()):
            contents = {}
            underlying = widget.layout().itemAt(i).widget().layout()
            commandle = underlying.itemAt(3).widget()
            arglw = underlying.itemAt(4).widget()
            kwarglw = underlying.itemAt(5).widget()
            command = commandle.text()
            if command:
                args = []
                kwargs = {}
                for j in range(arglw.count()):
                    arg = arglw.itemWidget(arglw.item(j)).text()
                    try:
                        arg = eval(arg)
                    except:
                        self.Alert('Assuming '+'"'+str(arg)+'"'+' is a string.')
                        arg = str(arg)
                    if isinstance(arg,str):
                        arg = "'''{}'''".format(arg)
                    args.append(arg)
                for j in range(kwarglw.count()):
                    key = kwarglw.itemWidget(kwarglw.item(j)).layout().itemAt(0).widget().text()
                    kwarg = kwarglw.itemWidget(kwarglw.item(j)).layout().itemAt(1).widget().text()
                    try:
                        kwarg = eval(kwarg)
                    except:
                        self.Alert('Assuming '+'"'+str(kwarg)+'"'+' is a string.')
                        kwarg = str(kwarg)
                    if isinstance(kwarg,str):
                        kwarg = "'''{}'''".format(kwarg)
                    kwargs[key]=kwarg
                contents['cmd'] = command
                contents['args'] = args
                contents['kwargs'] = kwargs
                commands.append(contents)
        self.getFromDict(keymap)['commands'] = commands
        self.preview()

        


def main():
    app = QApplication(sys.argv)
    frame = Pleditor()
    frame.show()
    retval = app.exec_()
    sys.exit(retval)


if __name__ == '__main__':
    main()