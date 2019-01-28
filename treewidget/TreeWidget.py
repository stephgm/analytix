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
                
def main():
    app = QApplication(sys.argv)
    frame = TreeModelTest()
    frame.show()
    retval = app.exec_()
    sys.exit(retval)


if __name__ == '__main__':
    main()
