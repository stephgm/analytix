#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 26 23:42:30 2019

@author: Jordan
"""

import os
import sys
import numpy as np
import pandas as pd
import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui
import PyQt5.QtGui as QtWidgets
from PyQt5.Qt import *
from PyQt5 import QtSql
from PyQt5.QtCore import QVariant
from PyQt5 import QtSql, uic, QtOpenGL


class TreeModelTest(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        uic.loadUi('TreeWidget.ui', self)
        
        self.dictionary = {'foo':
                            {'beez':
                                {'Bar':
                                    {'hoot':
                                        {'how':np.array([False]*100)}}},
                            'Baz':np.array([True]*1000)},
                        'hello':{ 
                                'faz':
                                    {'fiz':
                                        {'fooz':
                                            {'yeah':
                                                {'Thats':
                                                    {'right':np.array([True]*1000)},
                                                'wbb':np.array([True])}}}}}}
        self.setupTreeWidget()
#| Qt.ItemIsTristate
    def setupTreeWidget(self):
        def walkDict(d,parent):
            for k, v in d.items():
                child = QTreeWidgetItem(parent)
                child.setText(0,k)
                child.setCheckState(0, Qt.Unchecked)
                if isinstance(v, dict):
                    child.setFlags(child.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)
                    v = walkDict(v,child)
                else:
                    child.setFlags(child.flags() | Qt.ItemIsUserCheckable)
           
        for key in self.dictionary:  
            parent = QTreeWidgetItem(self.treeWidget)
            parent.setText(0,key)
            parent.setFlags(parent.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)
            if isinstance(self.dictionary[key],dict):
                walkDict(self.dictionary[key],parent)
        
        self.treeWidget.itemChanged.connect(self.handleItemChanged)
        
    def handleItemChanged(self, item, column):
        if item.flags() & QtCore.Qt.ItemIsUserCheckable:
            data = self.getTreePath(item)
            if item.checkState(0) == QtCore.Qt.Checked:
                if isinstance(data,np.ndarray):
                    print(data)
                else:
                    print('nope')
                
    def getTreePath(self, item):
        path = []
        while item is not None:
            path.append(str(item.text(0)))
            item = item.parent()
        path = reversed(path)
        for i,key in enumerate(path):
            if i == 0:
                data = self.dictionary[key]
            else:
                data = data[key]
            
        return data
    
    class LayeredTree(Widgets.QTreeWidget):
        checkChanged = Core.pyqtSignal(object)
        unCheckedChanged = Core.pyqtSignal(object)
        
        def __init__(self,parent=None,structure={},**kwargs):
            super(LayeredTree,self).__init__(parent)
            
            self.checkRoot = kwargs.get('checkRoot',False)
            self.allChecks = kwargs.get('allChecks',False)
            self.addChecks = kwargs.get('addChecks',True)
            
            self.parent = parent
            self.structure = structure
            self.makeTree()
            self.previousSelection = {}
            
            self.itemChanged.connect(lambda trash:self.getChecked())
            
        def makeTree(self):
            if isinstance(self.structure,dict):
                def walkDict(d,parent):
                    for k, v in d.items():
                        child = Widgets.QTreeWidgetItem(parent)
                        child.setText(0,k)
                        child.setCheckState(0, Core.Qt.Unchecked)
                        if isinstance(v, dict):
                            if self.addChecks:
                                child.setFlags(child.flags() | Core.Qt.ItemIsTristate | Core.Qt.ItemIsUserCheckable)
                            v = walkDict(v,child)
                        else:
                            if self.addChecks:
                                child.setFlags(child.flags() | Core.Qt.ItemIsUserCheckable)
                   
                for key in self.structure:  
                    parent = Widgets.QTreeWidgetItem(self)
                    parent.setText(0,key)
                    if self.checkRoot and self.addChecks:
                        parent.setFlags(parent.flags() | Core.Qt.ItemIsTristate | Core.Qt.ItemIsUserCheckable)
                        parent.setCheckState(0,Core.Qt.Unchecked)
                    if isinstance(self.structure[key],dict):
                        walkDict(self.structure[key],parent)
                    # else:
                    #     if self.addChecks:
                    #         parent.setFlags(parent.flags() | Core.Qt.ItemIsTristate | Core.Qt.ItemIsUserCheckable)
        
        def getChecked(self):
            if self.addChecks:
                paths = []
                newpaths = []
                for i in range(self.topLevelItemCount()):
                    item = self.topLevelItem(i)
                    def walkItems(treeitem):
                        if treeitem.childCount():
                            for j in range(treeitem.childCount()):
                                child = treeitem.child(j)
                                walkItems(child)
                        else:
                            if treeitem.checkState(0) != Core.Qt.Unchecked:
                                hasparent = True
                                path = treeitem.text(0)
                                parent = treeitem.parent()
                                while hasparent:
                                    if not parent:
                                        hasparent = False
                                    else:
                                        path = parent.text(0)+'/'+path
                                        parent = parent.parent()
                                paths.append(path)
                        
                    walkItems(item)
                if paths:
                    newpaths = []
                    for path in paths:
                        newpaths.append(path.split('/'))
                    print(newpaths)
                return newpaths
                
def main():
    app = QApplication(sys.argv)
    frame = TreeModelTest()
    frame.show()
    retval = app.exec_()
    sys.exit(retval)


if __name__ == '__main__':
    main()
