# -*- coding: utf-8 -*-
"""
Created on Tue Jun 11 14:16:07 2019

@author: DivollHJ
"""
import os
import sys
import cPickle
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

class Pleditor(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        uic.loadUi('Pleditor.ui', self)
        fname = 'C://Users//DivollHJ//Documents//Scripts//python//flashstuff//test.pklplt'
        d = cPickle.load(file(fname,'rb'))
        self.setupTreeWidget(self.PlotOptionsTree,d)
        
    def setupTreeWidget(self,widget,treedata):#,includelists):
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
#                if k not in includelist:
#                    continue
                child = QTreeWidgetItem(parent)
                if not isinstance(k,str):
                    k = str(k)
                child.setText(0,k)
                child.setCheckState(0, Qt.Unchecked)
                if isinstance(v, dict):
                    child.setFlags(child.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)
                    v = walkDict(v,child,key)
                #Line edit for single values
                if isinstance(v, str):
                    
#                if k in ['x label','y label','z label','plot title']:
                    self.nestedwidgets[key][k] = QLineEdit(v)
                    grandchild = QTreeWidgetItem(child)
                    widget.setItemWidget(grandchild,0,self.nestedwidgets[key][k])
                    self.nestedwidgets[key][k].textChanged.connect(lambda trash, plwidget=self.nestedwidgets[key][k],plindex=index,plkey=k:self.EditPlotOptions(plwidget,plindex,plkey,None))
                else:
                    pass
#                #Sliders for single values
#                if k in ['line width','bar width','bin num','alpha','markersize']:
#                    self.nestedwidgets[key][k] = QSlider(Qt.Horizontal)
#                    self.nestedwidgets[key][k].setMinimum(1)
#                    self.nestedwidgets[key][k].setMaximum(99)
#                    self.nestedwidgets[key][k].setValue(v)
#                    grandchild = QTreeWidgetItem(child)
#                    widget.setItemWidget(grandchild,0,self.nestedwidgets[key][k])
#                    self.nestedwidgets[key][k].valueChanged.connect(lambda plwidget=self.nestedwidgets[key][k],plindex=index,plkey=k:self.EditPlotOptions(plwidget,plindex,plkey,None))
#                #Combo Box for list values
#                if k in ['fill DA']:
#                    self.nestedwidgets[key][k]=[]                    
#                    self.nestedwidgets[key][k].append(QComboBox())
#                    self.nestedwidgets[key][k][-1].addItems(['True','False'])
#                    lsindex = self.nestedwidgets[key][k][-1].findText(str(d[k]))
#                    self.nestedwidgets[key][k][-1].setCurrentIndex(lsindex)
#                    grandchild = QTreeWidgetItem(child)
#                    widget.setItemWidget(grandchild,0,self.nestedwidgets[key][k][-1])
#                    activate = self.nestedwidgets[key][k][-1].currentText()
#                    self.nestedwidgets[key][k][-1].currentIndexChanged.connect(lambda trash, plwidget=self.nestedwidgets[key][k][-1],plindex=index,plkey=k:self.EditPlotOptions(plwidget,plindex,plkey,None))
#                if k in ['line style']:
#                    self.nestedwidgets[key][k] = []
#                    for i,item in enumerate(v):
#                        self.nestedwidgets[key][k].append(QComboBox())
#                        self.nestedwidgets[key][k][-1].clear()
#                        self.nestedwidgets[key][k][-1].addItems(linestyles)
#                        grandchild = QTreeWidgetItem(child)
#                        widget.setItemWidget(grandchild,0,self.nestedwidgets[key][k][-1])
#                        self.nestedwidgets[key][k][-1].currentIndexChanged.connect(lambda trash, plwidget=self.nestedwidgets[key][k][-1],plindex=index,plkey=k,pllistindex=i:self.EditPlotOptions(plwidget,plindex,plkey,pllistindex))
#                if k in ['marker','color']:
#                    self.nestedwidgets[key][k] = []
#                    mylayout = QVBoxLayout()
#                    for i,item in enumerate(v):
#                        self.nestedwidgets[key][k].append(QComboBox())
#                        self.nestedwidgets[key][k][-1].clear()
#                        if k == 'marker':
#                            container = 'markercontainer'
#                            self.nestedwidgets[key][k][-1].addItems(plotsymb)
#                        if k == 'color':
#                            container = 'colorcontainer'
#                            self.nestedwidgets[key][k][-1].addItems(plotcolor)
#                            if isinstance(item,str) or isinstance(item,unicode):
#                                lsindex = self.nestedwidgets[key][k][-1].findText(item)
#                                self.nestedwidgets[key][k][-1].setCurrentIndex(lsindex)
#                                self.nestedwidgets[key][k][-1].setEnabled(True)
#                            else:
#                                lsindex = self.nestedwidgets[key][k][-1].findText('COLORBAR')
#                                self.nestedwidgets[key][k][-1].setCurrentIndex(lsindex)
#                                self.nestedwidgets[key][k][-1].setEnabled(False)
#                        else: 
#                            lsindex = self.nestedwidgets[key][k][-1].findText(item)
#                            self.nestedwidgets[key][k][-1].setCurrentIndex(lsindex)
#                        mylayout.addWidget(self.nestedwidgets[key][k][-1])
#                        self.nestedwidgets[key][k][-1].currentIndexChanged.connect(lambda trash, plwidget=self.nestedwidgets[key][k][-1],plindex=index,plkey=k,pllistindex=i:self.EditPlotOptions(plwidget,plindex,plkey,pllistindex))
#                    self.nestedwidgets[key][container].setLayout(mylayout)
#                    grandchild = QTreeWidgetItem(child)
#                    widget.setItemWidget(grandchild,0,self.nestedwidgets[key][container])
#                #Line edit for list values
#                if k in ['legend']:
#                    container = 'legendcontainer'
#                    self.nestedwidgets[key][k] = []
#                    mylayout = QVBoxLayout()
#                    for i,item in enumerate(v):
#                        self.nestedwidgets[key][k].append(QLineEdit(item))
##                        grandchild = QTreeWidgetItem(child)
##                        widget.setItemWidget(grandchild,0,self.nestedwidgets[key][k][-1])
#                        self.nestedwidgets[key][k][-1].textChanged.connect(lambda trash, plwidget=self.nestedwidgets[key][k][-1],plindex=index,plkey=k,pllistindex=i:self.EditPlotOptions(plwidget,plindex,plkey,pllistindex))
#                        mylayout.addWidget(self.nestedwidgets[key][k][-1])
#                    self.nestedwidgets[key][container].setLayout(mylayout)
#                    grandchild = QTreeWidgetItem(child)
#                    widget.setItemWidget(grandchild,0,self.nestedwidgets[key][container])
#                
#                #Colorbar stuff
#                if k in ['colorbar']:
#                    intable = d['keyID'] in self.MasterData
#                    self.nestedwidgets[key][k]=[]
#                    #0 label
#                    self.nestedwidgets[key][k].append(QLabel('has colorbar:'))
#                    grandchild = QTreeWidgetItem(child)
#                    widget.setItemWidget(grandchild,0,self.nestedwidgets[key][k][-1])
#                    
#                    #1 has colorbar combo
#                    self.nestedwidgets[key][k].append(QComboBox())
#                    self.nestedwidgets[key][k][-1].addItems(['True','False'])
#                    lsindex = self.nestedwidgets[key][k][-1].findText(str(d['colorbar']))
#                    self.nestedwidgets[key][k][-1].setCurrentIndex(lsindex)
#                    grandchild = QTreeWidgetItem(child)
#                    widget.setItemWidget(grandchild,0,self.nestedwidgets[key][k][-1])
#                    activate = self.nestedwidgets[key][k][-1].currentText()
#                    self.nestedwidgets[key][k][-1].currentIndexChanged.connect(lambda trash, plwidget=self.nestedwidgets[key][k][-1],plindex=index,plkey=k,dictkey=key:self.handleColorbar(plwidget,plindex,plkey,dictkey))
#                    self.nestedwidgets[key][k][-1].currentIndexChanged.connect(lambda trash, plwidget=self.nestedwidgets[key][k][-1],plindex=index,plkey='colorbar':self.EditPlotOptions(plwidget,plindex,plkey,None))
#                    if not intable:
#                        self.nestedwidgets[key][k][-1].setEnabled(False)
#                    
#                    #2 label
#                    self.nestedwidgets[key][k].append(QLabel('color map header:'))
#                    grandchild = QTreeWidgetItem(child)
#                    widget.setItemWidget(grandchild,0,self.nestedwidgets[key][k][-1])
#                    
#                    #3 colorbar headers
#                    self.nestedwidgets[key][k].append(QComboBox())
#                    if intable:
#                        self.nestedwidgets[key][k][-1].addItems(d['non string headers'])
#                    else:
#                        self.nestedwidgets[key][k][-1].addItems([d['color map header']])
#                    lsindex = self.nestedwidgets[key][k][-1].findText(str(d['color map header']))
#                    self.nestedwidgets[key][k][-1].setCurrentIndex(lsindex)
#                    grandchild = QTreeWidgetItem(child)
#                    widget.setItemWidget(grandchild,0,self.nestedwidgets[key][k][-1])
#                    if activate == 'False':
#                        self.nestedwidgets[key][k][-1].setEnabled(False)
#                    if not intable:
#                        self.nestedwidgets[key][k][-1].setEnabled(False)
#                    self.nestedwidgets[key][k][-1].currentIndexChanged.connect(lambda trash, plwidget=self.nestedwidgets[key][k][1],plindex=index,plkey=k,dictkey=key:self.handleColorbar(plwidget,plindex,plkey,dictkey))
#                    self.nestedwidgets[key][k][-1].currentIndexChanged.connect(lambda trash,plwidget=self.nestedwidgets[key][k][-1],plindex=index,plkey='color map header':self.EditPlotOptions(plwidget,plindex,plkey,None))
#                    
#                    #4 label
#                    self.nestedwidgets[key][k].append(QLabel('color map name:'))
#                    grandchild = QTreeWidgetItem(child)
#                    widget.setItemWidget(grandchild,0,self.nestedwidgets[key][k][-1])
#                    
#                    #5 colorbar map
#                    self.nestedwidgets[key][k].append(QComboBox())
#                    self.nestedwidgets[key][k][-1].addItems(maps)
#                    lsindex = self.nestedwidgets[key][k][-1].findText(str(d['color map name']))
#                    self.nestedwidgets[key][k][-1].setCurrentIndex(lsindex)
#                    grandchild = QTreeWidgetItem(child)
#                    widget.setItemWidget(grandchild,0,self.nestedwidgets[key][k][-1])
#                    if activate == 'False':
#                        self.nestedwidgets[key][k][-1].setEnabled(False)
##                    if not intable:
##                        self.nestedwidgets[key][k][-1].setEnabled(False)
#                    self.nestedwidgets[key][k][-1].currentIndexChanged.connect(lambda trash, plwidget=self.nestedwidgets[key][k][1],plindex=index,plkey=k,dictkey=key:self.handleColorbar(plwidget,plindex,plkey,dictkey))
#                    self.nestedwidgets[key][k][-1].currentIndexChanged.connect(lambda trash,plwidget=self.nestedwidgets[key][k][-1],plindex=index,plkey='color map name':self.EditPlotOptions(plwidget,plindex,plkey,None))
#                    
#                    #6 label
#                    self.nestedwidgets[key][k].append(QLabel('colorbar label:'))
#                    grandchild = QTreeWidgetItem(child)
#                    widget.setItemWidget(grandchild,0,self.nestedwidgets[key][k][-1])
#                    
#                    #7 colorbar laabel
#                    self.nestedwidgets[key][k].append(QLineEdit(str(d['colorbar Label'])))
#                    grandchild = QTreeWidgetItem(child)
#                    widget.setItemWidget(grandchild,0,self.nestedwidgets[key][k][-1])
#                    if activate == 'False':
#                        self.nestedwidgets[key][k][-1].setEnabled(False)
#                    if not intable:
#                        self.nestedwidgets[key][k][-1].setEnabled(False)
##                    self.nestedwidgets[key][k][-1].editingFinished.connect(lambda trash, plwidget=self.nestedwidgets[key][k][1],plindex=index,plkey=k,dictkey=key:self.handleColorbar(plwidget,plindex,plkey,dictkey))
#                    self.nestedwidgets[key][k][-1].textChanged.connect(lambda trash, plwidget=self.nestedwidgets[key][k][-1],plindex=index,plkey='colorbar Label':self.EditPlotOptions(plwidget,plindex,plkey,None))
#                    
#                if k in ['symbol code']:
#                    intable = d['keyID'] in self.MasterData
#                    self.nestedwidgets[key][k]=[]
#                    self.nestedwidgets[key][k].append(QLabel('has symbol code:'))
#                    grandchild = QTreeWidgetItem(child)
#                    widget.setItemWidget(grandchild,0,self.nestedwidgets[key][k][-1])
#                    
#                    self.nestedwidgets[key][k].append(QComboBox())
#                    self.nestedwidgets[key][k][-1].addItems(['True','False'])
#                    lsindex = self.nestedwidgets[key][k][-1].findText(str(d['symbol code']))
#                    self.nestedwidgets[key][k][-1].setCurrentIndex(lsindex)
#                    grandchild = QTreeWidgetItem(child)
#                    widget.setItemWidget(grandchild,0,self.nestedwidgets[key][k][-1])
#                    activate = self.nestedwidgets[key][k][-1].currentText()
#                    self.nestedwidgets[key][k][-1].currentIndexChanged.connect(lambda trash, plwidget=self.nestedwidgets[key][k][-1],plindex=index,plkey=k,dictkey=key:self.handleSymbolCode(plwidget,plindex,plkey,dictkey))
#                    self.nestedwidgets[key][k][-1].currentIndexChanged.connect(lambda trash, plwidget=self.nestedwidgets[key][k][-1],plindex=index,plkey=k:self.EditPlotOptions(plwidget,plindex,plkey,None))
#                    if not intable:
#                        self.nestedwidgets[key][k][-1].setEnabled(False)
#                    
#                    self.nestedwidgets[key][k].append(QLabel('symbol code header:'))
#                    grandchild = QTreeWidgetItem(child)
#                    widget.setItemWidget(grandchild,0,self.nestedwidgets[key][k][-1])
#                    
#                    self.nestedwidgets[key][k].append(QComboBox())
#                    if intable:
#                        self.nestedwidgets[key][k][-1].addItems(d['unique headers'])
#                    else:
#                        self.nestedwidgets[key][k][-1].addItems([d['symbol code header']])
#                    lsindex = self.nestedwidgets[key][k][-1].findText(str(d['symbol code header']))
#                    self.nestedwidgets[key][k][-1].setCurrentIndex(lsindex)
#                    grandchild = QTreeWidgetItem(child)
#                    widget.setItemWidget(grandchild,0,self.nestedwidgets[key][k][-1])
#                    if activate == 'False':
#                        self.nestedwidgets[key][k][-1].setEnabled(False)
#                    if not intable:
#                        self.nestedwidgets[key][k][-1].setEnabled(False)
#                    self.nestedwidgets[key][k][-1].currentIndexChanged.connect(lambda trash, plwidget=self.nestedwidgets[key][k][1],plindex=index,plkey=k,dictkey=key:self.handleSymbolCode(plwidget,plindex,plkey,dictkey))
#                    self.nestedwidgets[key][k][-1].currentIndexChanged.connect(lambda trash,plwidget=self.nestedwidgets[key][k][-1],plindex=index,plkey='symbol code header':self.EditPlotOptions(plwidget,plindex,plkey,None))
#                    
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
#                includelist = includelists[i]
                walkDict(treedata[key],parent,key)
#        for i in range(2):
#            widget.resizeColumnToContents(i);
        widget.expandAll()
        widget.blockSignals(False)

def main():
    app = QApplication(sys.argv)
    frame = Pleditor()
    frame.show()
    retval = app.exec_()
    sys.exit(retval)


if __name__ == '__main__':
    main()