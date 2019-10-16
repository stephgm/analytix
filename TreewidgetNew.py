import sys
import PyQt5.QtWidgets as Widgets
import PyQt5.QtGui as Gui
import PyQt5.QtCore as Core
import PyQt5.uic as Qt5
import copy
import pandas as pd
import numpy as np
import glob
import re
from collections import Iterable

dictionary = {'foo':
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

def printit(x):
    print x

class CheckableTreeWidget(Widgets.QTreeWidget):
    itemSelected = Core.pyqtSignal(object)
    def __init__(self,dictionary, parent=None, **kwargs):
        super(CheckableTreeWidget,self).__init__(parent)

        if not isinstance(dictionary,dict):
            dictionary = {}

        self.getpath = kwargs.get('emitPath',True)
        self.checkedItems = []
        self.dictionary = dictionary
        self.setupTreeWidget()
#| Qt.ItemIsTristate
    def setupTreeWidget(self):
        def walkDict(d,parent):
            for k, v in d.items():
                child = Widgets.QTreeWidgetItem(parent)
                child.setText(0,k)
                child.setCheckState(0, Core.Qt.Unchecked)
                if isinstance(v, dict):
                    child.setFlags(child.flags() | Core.Qt.ItemIsTristate | Core.Qt.ItemIsUserCheckable)
                    v = walkDict(v,child)
                else:
                    child.setFlags(child.flags() | Core.Qt.ItemIsUserCheckable)

        for key in self.dictionary:
            parent = Widgets.QTreeWidgetItem(self)
            parent.setText(0,key)
            parent.setFlags(parent.flags() | Core.Qt.ItemIsTristate | Core.Qt.ItemIsUserCheckable)
            if isinstance(self.dictionary[key],dict):
                walkDict(self.dictionary[key],parent)

        self.itemChanged.connect(self.getSelectedItem)

    def getSelectedItem(self,item,column):
        path = []
        selected = []
        if not item.childCount():
            if self.getpath:
                while item:
                    path.insert(0,str(item.text(0)))
                    item = item.parent()
            else:
                selected.append(item.text(0))
            if self.getpath:
                self.itemSelected.emit(path)
            else:
                self.itemSelected.emit(selected)

    def getCurrentSelected

def main():
    app = Widgets.QApplication(sys.argv)
    frame = CheckableTreeWidget(dictionary,emitPath=False)
    frame.show()
    frame.itemSelected.connect(printit)
#    print frame.getTreePaths()
    retval = app.exec_()
    sys.exit(retval)
