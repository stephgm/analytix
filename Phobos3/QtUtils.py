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
import glob
import re
from collections import Iterable

if True:
### Common List Widget Functions

    def returnSelection(widget,**kwargs):
        sort = kwargs.pop('sort',False)
        getFirst = kwargs.pop('first',False)
        getLast = kwargs.pop('last',False)
        if isinstance(widget,Widgets.QListWidget) or isinstance(widget,Widgets.QTreeWidget):
            selection = [item.text() for item in widget.selectedItems()]
        else:
            return []
        if sort:
            selection.sort()
        if getFirst:
            if selection:
                return selection[0]
            else:
                return ''
        elif getLast:
            if selection:
                return selection[-1]
            else:
                return ''
        else:
            return selection

    def returnAllItems(widget,**kwargs):
        if not isinstance(widget,Widgets.QListWidget):
            return []

        getReadable = kwargs.get('readable',True)
        if getReadable:
            return [widget.item(i).text() for i in widget.count()]
        else:
            return [widget.item(i) for i in widget.count()]

### Search Bar
    class SearchBar(Widgets.QWidget):
        def __init__(self,widget=None,parent=None,**kwargs):
            super(SearchBar,self).__init__(parent)
            self.parent = parent
            self.widget = widget

            self.GroupRadials = self.makeGroup()

            self.searchLabel = Widgets.QLabel('Search')
            self.searchLine = Widgets.QLineEdit()
            self.searchlayout = Widgets.QGridLayout()
            self.searchlayout.addWidget(self.searchLabel,0,0)
            self.searchlayout.addWidget(self.searchLine,0,1)
            self.searchlayout.addWidget(self.GroupRadials,1,0,1,2)
            self.setLayout(self.searchlayout)

            self.makeConnections()

        def makeConnections(self):
            self.searchLine.textChanged.connect(self.searchFunction)

        def makeGroup(self):
            group = Widgets.QGroupBox()
            grouplayout = Widgets.QGridLayout()
            self.StringMatch = Widgets.QRadioButton('String Matching')
            self.Regex = Widgets.QRadioButton('Regex')
            grouplayout.addWidget(self.StringMatch,0,0)
            grouplayout.addWidget(self.Regex,0,1)
            group.setLayout(grouplayout)
            self.StringMatch.setChecked(True)
            return group

        def searchFunction(self,text):
            if self.widget:
                if isinstance(self.widget,Widgets.QListWidget):
                    for i in xrange(self.widget.count()):
                        if self.StringMatch.isChecked():
                            self.widget.item(i).setHidden(text.lower() not in self.widget.item(i).text().lower())
                        elif self.Regex.isChecked():
                            try:
                                if not re.match(text.lower(),self.widget.item(i).text().lower()):
                                    self.widget.item(i).setHidden(True)
                                else:
                                    self.widget.item(i).setHidden(False)
                            except:
                                pass
                elif isinstance(self.widget,Widgets.QComboBox):
                    #TODO maybe this works?
                    #Variable getfirst is to get the first index that isn't hidden
                    getfirst = None
                    if self.StringMatch.isChecked():
                        idx = pd.Series([True if text.lower() not in self.widget.itemText(k).lower() else False for k in xrange(self.widget.count())])
                    elif self.Regex.isChecked():
                        try:
                            idx = pd.Series([True if not re.match(text.lower(),self.widget.itemText(k).lower()) else False for k in xrange(self.widget.count())])
                        except:
                            map(lambda x:self.widget.view().setRowHidden(False,x),xrange(self.widget.count()))
                            return
                    map(lambda x,y:self.widget.view().setRowHidden(x,y),idx.index,idx)
                    index = (idx.values == False).argmax()
                    if index == 0 and idx[0]:
                        index = -1
                    self.widget.setCurrentIndex(index)
            else:
                print('Uh oh!  You forgot to set a widget')

### Event/Run Oriented pop-ups
    def openRunListWidget(rdir,**kwargs):
        title = kwargs.get('title','Select Runs')
        selectionType = kwargs.get('selection',1)
        search = kwargs.get('search',True)

        widget = Widgets.QDialog()
        buttonBox = Widgets.QDialogButtonBox(widget)
        layout = Widgets.QGridLayout()
        listWidget = Widgets.QListWidget()
        selectAll = Widgets.QPushButton('Select All')
        selectAll.clicked.connect(listWidget.selectAll)
        if search:
            searchbar = SearchBar(listWidget,widget)
            layout.addWidget(searchbar)
        layout.addWidget(listWidget)

        layout.addWidget(selectAll)
        layout.addWidget(buttonBox)
        widget.setLayout(layout)

        if selectionType == 0:
            listWidget.setSelectionMode(Widgets.QAbstractItemView.SingleSelection)
        elif selectionType == 1:
            listWidget.setSelectionMode(Widgets.QAbstractItemView.MultiSelection)
        elif selectionType == 2:
            listWidget.setSelectionMode(Widgets.QAbstractItemView.ExtendedSelection)
        buttonBox.setStandardButtons(Widgets.QDialogButtonBox.Ok | Widgets.QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(widget.accept)
        buttonBox.rejected.connect(widget.reject)
        if os.path.isdir(rdir):
            runs = glob.glob(os.path.join(rdir,'*[0-9].[0-9]'))
            runs = map(os.path.basename,runs)
            listWidget.addItems(runs)

        retval = widget.exec_()

        # 1 is if Ok is pushed... 0 for cancel or 'X'
        if retval == 1:
            return returnSelection(listWidget)
        else:
            return []



### Open File Functions

    def openSingleFile(**kwargs):
        caption = kwargs.pop('caption','Open File')
        directory = kwargs.pop('directory',os.getcwd())
        extensions = kwargs.pop('extensions',{'All Files':['*']})
        if not isinstance(caption,str):
            print("The caption argument passed is not a string. Defaulting to 'Open File'")
            caption = 'Open File'
        if not isinstance(directory,str) and not os.path.isdir(directory):
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
            if ns.endswith(';; '):
                ns = ns[:-3]
        try:
            fname = Widgets.QFileDialog.getOpenFileName(None,caption,directory,ns)[0]
        except:
            print("The format of the extensions was not correct\nAn example of correct usage would be {'All Files':[''],'Images':['.jpg','.png','.img']} \n")
            fname = Widgets.QFileDialog.getOpenFileName(None,caption,directory,"All Files (*)")
        return fname

    def openMultipleFiles(**kwargs):
        caption = kwargs.pop('caption','Open Files')
        directory = kwargs.pop('directory',os.getcwd())
        extensions = kwargs.pop('extensions',{'All Files':['*']})
        if not isinstance(caption,str):
            print("The caption argument passed is not a string. Defaulting to 'Open Files'")
            caption = 'Open File'
        if not isinstance(directory,str) and not os.path.isdir(directory):
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
            if ns.endswith(';; '):
                ns = ns[:-3]
        try:
            fname = Widgets.QFileDialog.getOpenFileNames(None,caption,directory,ns)[0]
        except:
            print("The format of the extensions was not correct\nAn example of correct usage would be {'All Files':[''],'Images':['.jpg','.png','.img']} \n")
            fname = Widgets.QFileDialog.getOpenFileNames(None,caption,directory,"All Files (*)")
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

### Warning Messages

    def MessageBox(MessageText,**kwargs):

        '''
        Pops up a dialog box.  Returns True or False based on what the user has clicked.
        This allows you to either halt code or continue going based on the user's decision.

        TODO could change icon in kwargs, but seems to fancy for now... function/form

        Input:
                MessageText - The message you want the user to see on popup
        Kwargs:
                title - set the window title
                detail - the detailed message when you click show details
                informative - the text that appears below the message text
                showinforma - choose whether or not to show any informative text
        Return:
                True - if Ok Button is clicked
                False - if Cancel or "x" is clicked
        '''

        title = kwargs.get('title','Warning Message')
        detailed = kwargs.get('detail','There is no detailed information')
        informative = kwargs.get('informative','No further information to give')
        showinformative = kwargs.get('showinform',False)
        msg = Widgets.QMessageBox()
        msg.setIcon(Widgets.QMessageBox.Information)
        if not isinstance(MessageText,basestring):
            MessageText = 'Something went wrong'
        msg.setText(MessageText)
        if showinformative:
            msg.setInformativeText(informative)
        msg.setWindowTitle(title)
        msg.setDetailedText(detailed)
        msg.setStandardButtons(Widgets.QMessageBox.Ok | Widgets.QMessageBox.Cancel)

        retval = msg.exec_()
        if retval == Widgets.QMessageBox.Ok:
            return True
        else:
            return False

### Table Model

    class EpicTableModel(Core.QAbstractTableModel):
        def __init__(self, datain={}, parent=None, *args,**kwargs):
            Core.QAbstractTableModel.__init__(self, parent, *args)

            self.edit = kwargs.get('editable',False)
            if not isinstance(self.edit,bool):
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

class PandasCSVopener(Widgets.QWidget):
    done = Core.pyqtSignal(object)
    def __init__(self,fpath,parent=None,**kwargs):
        super(PandasCSVopener,self).__init__(parent)
        if not os.path.isfile(fpath):
            print('{} is not a valid file'.format(fpath))
            self.close()
        self.parent = parent
        self.fpath = fpath
        self.setWindowTitle('CSV Open Previewer')
        self.y = pd.DataFrame()

        self.makeWidget()
        self.makeConnections()
        self.preview()

    def makeConnections(self):
        self.SepSelection.editingFinished.connect(lambda:self.preview())
        self.changeHeaders.toggled.connect(self.addHeaderWidgets)
        self.addHeaders.toggled.connect(self.addHeaderWidgets)
        self.changeHeaders.toggled.connect(lambda:self.handleCheckBoxes('change'))
        self.addHeaders.toggled.connect(lambda:self.handleCheckBoxes('add'))

    def handleCheckBoxes(self,text):
        if text == 'add':
            if self.addHeaders.isChecked():
                self.changeHeaders.blockSignals(True)
                self.changeHeaders.setChecked(False)
                self.changeHeaders.blockSignals(False)
        elif text == 'change':
            if self.changeHeaders.isChecked():
                self.addHeaders.blockSignals(True)
                self.addHeaders.setChecked(False)
                self.addHeaders.blockSignals(False)
        self.preview()

    def makeWidget(self):
        self.layout = Widgets.QGridLayout()
        self.SepLabel = Widgets.QLabel('Separator:')
        self.SepSelection = Widgets.QLineEdit(',')
        self.changeHeaders = Widgets.QCheckBox('Change Headers')
        self.addHeaders = Widgets.QCheckBox('Add Headers')
        self.previewTable = Widgets.QTableWidget()
        self.setLayout(self.layout)
        self.layout.addWidget(self.SepLabel,0,0)
        self.layout.addWidget(self.SepSelection,0,1)
        self.layout.addWidget(self.changeHeaders,1,0)
        self.layout.addWidget(self.addHeaders,1,1)

        self.layout.addWidget(self.previewTable,1000,0,1,2)
        self.buttonBox = Widgets.QDialogButtonBox()
        self.buttonBox.setStandardButtons(Widgets.QDialogButtonBox.Ok | Widgets.QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.layout.addWidget(self.buttonBox,1001,0)

    def addHeaderWidgets(self,show):
        try:
            for i in range(len(self.newlabel)):
                self.newlabel[i].deleteLater()
                self.origlabel[i].deleteLater()
            self.newlabel = []
            self.origlabel = []
        except:
            pass
        if show:
            if self.y.shape[0]:
                self.newlabel = []
                self.origlabel = []
                for i,header in enumerate(list(self.y)):
                    self.origlabel.append(Widgets.QLabel(header))
                    self.newlabel.append(Widgets.QLineEdit(header))
                    self.newlabel[-1].editingFinished.connect(lambda:self.preview())
                    self.layout.addWidget(self.origlabel[-1],i+2,0)
                    self.layout.addWidget(self.newlabel[-1],i+2,1)
        self.preview()

    def preview(self):
        sep = self.SepSelection.text()
        if not sep:
            sep = ' '
        if not self.addHeaders.isChecked() and not self.changeHeaders.isChecked():
            self.y = pd.read_csv(self.fpath,sep=sep)
        elif self.addHeaders.isChecked() and not self.changeHeaders.isChecked():
            self.y = pd.read_csv(self.fpath,sep=sep,names=[header.text() for header in self.newlabel])
        elif self.changeHeaders.isChecked() and not self.addHeaders.isChecked():
            self.y = pd.read_csv(self.fpath,sep=sep).rename(columns={oheader.text():header.text() for oheader,header in zip(self.origlabel,self.newlabel)})
        self.previewTable.setRowCount(10)
        self.previewTable.setColumnCount(self.y.shape[1])
        self.previewTable.setHorizontalHeaderLabels(list(self.y))
        for row in range (0, self.y.shape[0]):
            for col in range (0, self.y.shape[1]):
                    data = str(self.y.iloc[row, col] )
                    self.previewTable.setItem(row, col, Widgets.QTableWidgetItem(str(data)))

    def accept(self):
        self.done.emit(self.y)
        self.close()

    def reject(self):
        self.done.emit(None)
        self.close()


if __name__ == '__main__':
    try:
        def showdata(data):
            print(data)
        path = pathtocsv
        x = PandasCSVopener(path)
        x.done.connect(showdata)
        x.show()
    except:
        pass