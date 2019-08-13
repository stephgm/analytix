# -*- coding: utf-8 -*-
"""
Created on Wed Jul 24 18:36:57 2019

@author: Jordan
"""

import sys
import os

import PyQt5.QtWidgets as Widgets
import PyQt5.QtGui as Gui
import PyQt5.QtCore as Core
import PyQt5.uic as Qt5
import copy
import pandas as pd
from collections import Iterable

### Common List Widget Functions

def returnSelection(widget,**kwargs):
    sort = kwargs.pop('sort',False)
    if isinstance(widget,Widgets.QListWidget) or isinstance(widget,Widgets.QTreeWidget):
        selection = [item.text() for item in widget.selectedItems()]
    else:
        return []
    if sort:
        selection.sort()
    return selection

### Open File Functions

def openSingleFile(**kwargs):
    caption = kwargs.pop('caption','Open File')
    directory = kwargs.pop('directory',os.getcwd())
    extensions = kwargs.pop('extensions',{'All Files':['*']})
    if not isinstance(caption,str):
        print("The caption argument passed is not a string. Defaulting to 'Open File'")
        caption = 'Open File'
    if not os.path.isdir(directory):
        print("The Directory argument passed is not a directory. Defaulting to working directory")
        directory = os.getcwd()
    if not isinstance(extensions,dict):
        print("The extensions argument passed is not a dictionary\n \
              An example of correct usage would be {'All Files':[''],'Images':['.jpg','.png','.img']} \n \
              Defaulting to All Files")
        ns = ("All Files (*)")
    else:
        ns = ''
        for key in extensions:
            ns = ns+str(key)+' ('
            for string in extensions[key]:
                ns = ns+' *'+str(string)
            ns = ns+');; '
        ns = ns
    fname = Widgets.QFileDialog.getOpenFileName(None,caption,directory,ns)[0]
    return fname

def openMultipleFiles(**kwargs):
    caption = kwargs.pop('caption','Open Files')
    directory = kwargs.pop('directory',os.getcwd())
    extensions = kwargs.pop('extensions',{'All Files':['*']})
    if not isinstance(caption,str):
        print("The caption argument passed is not a string. Defaulting to 'Open Files'")
        caption = 'Open File'
    if not os.path.isdir(directory):
        print("The Directory argument passed is not a directory. Defaulting to working directory")
        directory = os.getcwd()
    if not isinstance(extensions,dict):
        print("The extensions argument passed is not a dictionary\n \
              An example of correct usage would be {'All Files':[''],'Images':['.jpg','.png','.img']} \n \
              Defaulting to All Files")
        ns = ("All Files (*)")
    else:
        ns = ''
        for key in extensions:
            ns = ns+str(key)+' ('
            for string in extensions[key]:
                ns = ns+' *'+str(string)
            ns = ns+');; '
        ns = ns
    fname = Widgets.QFileDialog.getOpenFileNames(None,caption,directory,ns)[0]
    return fname

def openFileWithFunction(function,*args):
     return function(*args)
    
### Drag and Drop Methods
def dragEnterEvents(e):
    if e.mimeData().hasText():
        e.accept()
    else:
        e.ignore()
    
def dropText(event):
    if event.mimeData().hasText():
        return event.mimeData().text()
    else:
        print('The dropped item does not have any text associated with it')
        return ''

def dropFileDir(event):
    paths = []
    if event.mimeData().hasUrls():
        text = event.mimeData().text()
        prepaths = text.split('\n')
        for path in prepaths:
            if 'file:' in path:
                paths.append(path.replace('file:/','').strip())
        return paths
    else:
        print('The dropped item(s) have no url data')
        return paths
    

        
def testfunc(first1,first2):
    print first1
    print first2
openFileWithFunction(testfunc,'thisfile','thatfile')


def Alert(statusbar,msg, **kwargs):
    if not isinstance(statusbar,Widgets.QStatusBar):
        print('The passed widget is not a QStatusBar type widget, returning')
        return
    if not isinstance(msg,str):
        print('The passed message is not a string type, returning')
        
    StyleSheetString = 'QStatusBar{padding-left:8px;'
        
    color = kwargs.get('color','black')
    if not isinstance(color,str):
        print('The passed color is not a string, setting to "black"')
        color = 'black'
    StyleSheetString += 'color:{};'.format(color)
    bold = kwargs.get('bold',False)
    if not isinstance(bold,bool):
        print('The passed bold kwarg is not a boolean type, setting to False')
        bold = False
    if bold:
        StyleSheetString += 'font-weight:bold;'
    background = kwargs.get('background','rgba(255,255,255,255)')
    if not isinstance(background,str):
        print('The passed background was not a string, setting to "rgba(255,255,255,255)"')
        background = 'rgba(255,0,0,255)'
    StyleSheetString += 'background:{};'.format(background)
    wtime = kwargs.get('time',5)
    if not isinstance(wtime,int):
        print('The wtime given should be in seconds and of type int, setting to -1')
        wtime = -1
    if wtime != -1:
        msecs = wtime*1000
    error = kwargs.get('error',False)
    if not isinstance(error,bool):
        print('The error command passed is not of type bool, but since you passed something assuming True')
        error = True
    if error:
        StyleSheetString = 'QStatusBar{padding-left:8px;font-weight:bold;color:red;background:'+background+'}'
        statusbar.setStyleSheet(StyleSheetString)
        statusbar.showMessage('ERROR: '+msg,10000)
        
    else:
        statusbar.setStyleSheet(StyleSheetString+"}")
        statusbar.showMessage(msg,msecs)
        
class EpicTableModel(Core.QAbstractTableModel):
    def __init__(self, datain={}, parent=None, *args,**kwargs):
        Core.QAbstractTableModel.__init__(self, parent, *args)
        
        self.edit = kwargs.get('editable',False)
        if not isinstance(edit,bool):
            self.edit = False
        self.highlight = kwargs.get('highlight',False)
        if not isinstance(highlight,bool):
            self.highlight = False
            
        if not isinstance(datain,pd.DataFrame):
            datain = pd.DataFrame()
            
        self.header = list(datain)
        
        self.UntouchedData = copy.deepcopy(datain)
        self.arraydata = copy.deepcopy(datain)
        self.origdata = copy.deepcopy(datain)
            
    def rowCount(self, parent):
        return self.arraydata.shape[0]

    def columnCount(self, parent):
        return self.arraydata.shape[1]

    def headerData(self, section, orientation, role):
        if role == Core.Qt.DisplayRole:
            if orientation == Core.Qt.Horizontal:
                return self.header[section]
            else:
                return section

    def flags(self, index):
        if self.edit:
            return Core.Qt.ItemIsEnabled | Core.Qt.ItemIsEditable | Core.Qt.ItemIsSelectable
        else:
            return Core.Qt.ItemIsEnabled | Core.Qt.ItemIsSelectable

    def data(self, index, role):
        if not index.isValid():
            return None
        if role == Core.Qt.DisplayRole:
            value = self.arraydata[self.header[index.column()]][index.row()]
            return value
        if role == Core.Qt.BackgroundRole:
            for header in self.colorcell['colorcell'][index.row()]:
                if header == self.header[index.column()]:
                    return Gui.QBrush(Core.Qt.red)
    
    def getTableData(self):
        return self.arraydata
    
    def getHeaderNames(self):
        return self.header
    
class Plotter(Widgets.QMainWindow):
    def __init__(self, parent=None):
        super(Plotter,self).__init__(parent)
        Widgets.QMainWindow.__init__(self, parent)
        Qt5.loadUi('Test.ui', self)
        self.MyListWidget.dragEnterEvent = dragEnterEvents
        self.MyListWidget.dropEvent = self.ListDropEvent
        self.MyListWidget.addItems([str(i) for i in range(10)])
        self.makeConnections()
        Alert(self.statusbar,'Hey there',bold=True)
#        files = openMultipleFiles(extensions={'Pictures':['.png'],'H5':['.h5'],'Jpeg':['.jpg']})
#        print files
        
    def makeConnections(self):
        self.pushButton.clicked.connect(lambda:self.Printing())
    
    def Printing(self):
        Alert(self.statusbar,'Yo',error=True,background='rgba(0,0,0,255)')
        print returnSelection(self.MyListWidget)
#        self.layout.addWidget(StandardListWidget(self))
    
    def ListDropEvent(self,event):
        
        self.MyListWidget.clear()
        paths = dropFileDir(event)
        self.MyListWidget.addItems(paths)
        print paths
        
def main():
    app = Widgets.QApplication(sys.argv)
    frame = Plotter()
    frame.show()
#    splash.finish(frame)
    retval = app.exec_()
    sys.exit(retval)
    
if __name__ == '__main__':
    main()