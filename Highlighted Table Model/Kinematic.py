# -*- coding: utf-8 -*-
"""
Created on Sat Feb  2 01:55:11 2019

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

class Kinematic(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        uic.loadUi('Kinematic.ui', self)
        self.splitter_2.setSizes([50,600])
        self.splitter.setSizes([150,800])
        
        
        # Mock Data
        z = {}
        z['this'] = np.array([np.random.randint(0,100)]*50)
        z['that'] = np.array([np.random.randint(0,100)]*50)
        z['fun'] = np.array([np.random.randint(0,100)]*50)
        data = pd.DataFrame(z)
        headers = list(data)
        
        #A numpy array telling which column of the row needs to be filled in.
        #This is just a list of lists of headers, then turned into dataframe.
        #This is so multiple headers can be filled in.
        colorcell = {}
        colorcell['colorcell'] = []
        for i in range(len(z['this'])):
            colorcell['colorcell'].append([headers[np.random.randint(0,3)]])
        colorcell = pd.DataFrame(colorcell)
        self.tableView.setModel(FieldTableModel(data,colorcell,list(data),self.tableView))
        
class FieldTableModel(QAbstractTableModel):
    def __init__(self, datain={}, colorcell = {}, header=[], parent=None, *args):
        QAbstractTableModel.__init__(self, parent, *args)
        self.arraydata = copy.deepcopy(datain.astype(str))
        self.colorcell = colorcell
        self.header = header
        self.parent = parent
        
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
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def data(self, index, role):
        if not index.isValid():
            return None
        if role == Qt.DisplayRole:
            value = self.arraydata[self.header[index.column()]][index.row()]
            return value
        if role == QtCore.Qt.BackgroundRole:
            for header in self.colorcell['colorcell'][index.row()]:
                if header == self.header[index.column()]:
                    return QtGui.QBrush(QtCore.Qt.red)
    
    def getTableData(self):
        return self.arraydata
    
    def getHeaderNames(self):
        return self.header
        
def main():
    app = QApplication(sys.argv)
    frame = Kinematic()
    frame.show()
    retval = app.exec_()
    sys.exit(retval)


if __name__ == '__main__':
    main()