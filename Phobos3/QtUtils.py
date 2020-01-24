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

#TODO these need to be made like at work with file imports
sys.path.append('/home/klinetry/Desktop/Phobos3')
import PhobosFunctions as PF
import PhobosHelper as PH

if True:

### Spacer Items
    vSpacer = Widgets.QSpacerItem(1,1,Widgets.QSizePolicy.Fixed,Widgets.QSizePolicy.Expanding)
    hSpacer = Widgets.QSpacerItem(1,1,Widgets.QSizePolicy.Expanding,Widgets.QSizePolicy.Fixed)
### Common List Widget Functions
    class StringListWidget(Widgets.QWidget):
        '''
        Widget that is meant to be within a GUI.

        Purpose:
            Creates a list widget with a search bar that can filter the items inside.

        Signals:
            getSelection - Emits a signal whenever the button at the bottom of the
                            widget is clicked.  This will emit a list of selected
                            items.

            updated -       Emits a signal whenever the setList method is called.
                            This means that the list widget has been updated.  This
                            will emit a blank signal.

        Input:
                listItems - The list of strings that you want to display
                parent - The widget that this widget will be the child of

        Kwargs:
                OKname - The name of the OK button.  Set this to suite your needs.
                selectAll - Add a select all button that will select all.
                selection - 0 = single selection
                            1 = multi selection
                            2 = extended selection

        The items can be updated by calling setList(NewList)

        '''
        getSelection = Core.pyqtSignal(object)
        updated = Core.pyqtSignal()
        def __init__(self,listItems=[],parent=None,**kwargs):
            super(StringListWidget,self).__init__(parent)
            self.n = self.__class__.__name__
            self.parent = parent
            self.listItems = listItems
            if not isinstance(self.listItems[0],basestring):
                print('listItems passed to {}, were not string types, program will Fail shortly :D'.format(self.n))
            self.OKname = kwargs.get('OKname','Confirm')
            if not isinstance(self.OKname,basestring):
                print('OKname kwarg was not set to a string, setting to Confirm.  From: {}'.format(self.n))
                self.OKname = 'Confirm'
            self.selectionType = kwargs.get('selection',0)
            self.addSelectAll = kwargs.get('selectAll',True)
            self.makeWidget()

        def makeWidget(self):
            self.layout = Widgets.QGridLayout()
            self.setLayout(self.layout)
            self.ListWidget = Widgets.QListWidget()
            if self.selectionType == 0:
                self.ListWidget.setSelectionMode(Widgets.QAbstractItemView.SingleSelection)
            elif self.selectionType == 1:
                self.ListWidget.setSelectionMode(Widgets.QAbstractItemView.MultiSelection)
            elif self.selectionType == 2:
                self.ListWidget.setSelectionMode(Widgets.QAbstractItemView.ExtendedSelection)
            self.ListWidget.addItems(self.listItems)
            self.SearchBar = SearchBar(self.ListWidget,self,regex=False)
            self.OKButton = Widgets.QPushButton(self.OKname)
            self.OKButton.clicked.connect(lambda:self.addSelected())
            self.layout.addWidget(self.SearchBar)
            self.layout.addWidget(self.ListWidget)
            if self.addSelectAll:
                self.SelectAllButton = Widgets.QPushButton('Select All')
                self.SelectAllButton.clicked.connect(self.ListWidget.selectAll)
                self.layout.addWidget(self.SelectAllButton)
            self.layout.addWidget(self.OKButton)

        def setList(self,items):
            if not isinstance(items,list):
                print('items passed to setList in {}, was not a list.  Returning'.format(self.n))
                return
            if not isinstance(items[0],basestring):
                print('items passed to setList in {}, were not string types.  Returning'.format(self.n))
                return
            self.ListWidget.clear()
            self.listItems = copy.copy(items)
            self.ListWidget.addItems(self.listItems)
            self.updated.emit()

        def addSelected(self):
            selectedHeaders = returnListSelection(self.ListWidget)
            self.getSelection.emit(selectedHeaders)


    def returnListSelection(widget,**kwargs):
        '''
        Returns a list of the selected items in a ListWidget or TreeWidget

        Input:
                widget - The widget in which to return the selection from

        Kwargs:
                sort - return a sorted list of the selected items
                first - return the first selected item
                last - return the last selected item
                readable - return readable text of the item.  If False, return just the item (Which should work for non string items too)
        Return:
                Returns a list of selected items
        '''
        sort = kwargs.pop('sort',False)
        getFirst = kwargs.pop('first',False)
        getLast = kwargs.pop('last',False)
        getReadable = kwargs.get('readable',True)
        if getReadable and isinstance(widget,Widgets.QListWidget) or isinstance(widget,Widgets.QTreeWidget):
            selection = [str(item.text()) for item in widget.selectedItems()]
        elif not getReadable and isinstance(widget,Widgets.QListWidget) or isinstance(widget,Widgets.QTreeWidget):
            sort = False
            selection = [item for item in widget.selectedItems()]
        else:
            return []
        if sort:
            selection = sorted(selection)
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

    def returnAllListItems(widget,**kwargs):
        '''
        Returns all items within a ListWidget

        Input:
                widget - The list widget in which to grab all the items

        Kwargs:
                readable - returns the text of the item inside the widget, else
                            returns the item object.
        Return:
                Returns the list of all items in the widget.
        '''
        if not isinstance(widget,Widgets.QListWidget):
            return []

        getReadable = kwargs.get('readable',True)
        if getReadable:
            return [str(widget.item(i).text()) for i in xrange(widget.count())]
        else:
            return [widget.item(i) for i in xrange(widget.count())]

### Common Table View/Widget Functions
    class StatTable(Widgets.QWidget):
        '''
        Purpose:
            This will take in some data, and calculate some statistics on it.
            The height is fixed currently to show ALL of the rows without creating a
            scroll bar for the user.  That way everything can be seen at a glance.

        Signals:
            Showing - Emits a bool signal for if the widget is hiding or showing
            Updated - Emits a signal for when the statistics are updated.

        Inputs:
                Data - A pandas dataframe with the data you want to take statistics of
                parent - The parent widget that this widget will reside in
        Kwargs:
                setH - An integer to set the height of the widget to.
                       For 8 rows, 325 is the perfect amount to show without scrolling


        '''

        Showing = Core.pyqtSignal(bool)
        Updated = Core.pyqtSignal()
        def __init__(self,data=pd.DataFrame(),parent=None,**kwargs):
            super(StatTable,self).__init__(parent)
            self.n = self.__class__.__name__
            self.parent = parent

            self.setHeight = kwargs.get('setH',325)
            if not isinstance(self.setHeight,int):
                print('The setH kwarg you gave is not an int. From: {}'.format(self.n,))
                self.setHeight = 325
            self.setFixedHeight(self.setHeight)

            self.makeWidget()
            self.calcStats(data)

        def makeWidget(self):
            self.Table = Widgets.QTableView()

        def calcStats(self,data):
            features = ['# of Unique Vals','Max','25%','50%','75%','Min','Mean','Std. Dev.','Most Frequent']
            if not isinstance(data,pd.DataFrame):
                print('The data passed to the calcStats function in {} was not a pandas DataFrame. Returning'.format(self.n))
                return
            statdat = pd.DataFrame(index=features,columns=list(data))
            for header in list(data):
                statdat[header].iloc[0] = len(pd.unique(data[header]))
                if data[header].dtype.kind not in ['O','b']:
                    statdat[header].iloc[1] = data[header].max()
                    statdat[header].iloc[2] = data[header].quantile(.25)
                    statdat[header].iloc[3] = data[header].quantile(.5)
                    statdat[header].iloc[4] = data[header].quantile(.75)
                    statdat[header].iloc[5] = data[header].min()
                    statdat[header].iloc[6] = data[header].mean()
                    statdat[header].iloc[7] = data[header].std()
                else:
                    statdat[header].iloc[1] = 'N/A'
                    statdat[header].iloc[2] = 'N/A'
                    statdat[header].iloc[3] = 'N/A'
                    statdat[header].iloc[4] = 'N/A'
                    statdat[header].iloc[5] = 'N/A'
                    statdat[header].iloc[6] = 'N/A'
                    statdat[header].iloc[7] = 'N/A'
                statdat[header].iloc[8] = data[header].astype(str).value_counts().idxmax()
            self.model = PH.PhobosTableModel(statdat,self,rowLabels=features)
            self.Table.setModel(self.model)
            self.Updated.emit()

        def showing(self,choice):
            if choice:
                self.show()
            else:
                self.hide()
            self.Showing.emit(choice)



    def returnTableSelectedColumns(widget,**kwargs):
        '''
        This function returns a TableView or TableWidget selected columns.  The whole
        column has to be selected for it to register.  The return values will be the
        horizontal headers names along the top of the table.

        Input:
                widget - The tableview or tablewidget that you wish to return the selection from

        Kwargs:
                sort - Sort the returned selection
                first - Grab the first selected column
                last - Grab the last selected column
                index - Returns the index item of the widget.  (Not sure why you would want this, but it's here)

        Return:
            Returns a list of columns that are selected by the user.
        '''
        sort = kwargs.get('sort',False)
        getFirst = kwargs.get('first',False)
        getLast = kwargs.get('last',False)
        indexOnly = kwargs.get('index',False)
        if isinstance(widget,Widgets.QTableView) or isinstance(widget,Widgets.QTableWidget):
            if isinstance(widget,Widgets.QTableWidget):
                if not indexOnly:
                    selection = [str(widget.horizontalHeaderItem(index.column()).text())\
                                 for index in widget.selectionModel().selectedColumns()]
                else:
                    selection = [index.column() for index in widget.selectionModel().selectedColumns()]
            else:
                try:
                    if not indexOnly:
                        selection = [str(widget.model().headerData(index.column())) \
                                     for index in widget.selectionModel().selectedColumns()]
                    else:
                        selection = [index.column() for index in widget.selectionModel().selectedColumns()]
                except:
                    print('Could not get selection from TableView.  Look at the headerData function there and set orientation and role to named arguments')
                    return []
            if selection:
                if sort:
                    selection = sorted(selection)
                if getFirst:
                    return selection[0]
                elif getLast:
                    return selection[-1]
                else:
                    return selection
        else:
            return []

    def returnTableSelectedRows(widget,**kwargs):
        '''
        This function returns a TableView or TableWidget selected Rows.  The whole
        row has to be selected for it to register.  The return values will be the
        vertical headers names along the side of the table.  This normally corresponds
        to the row number.

        Input:
                widget - The tableview or tablewidget that you wish to return the selection from

        Kwargs:
                sort - Sort the returned selection
                first - Grab the first selected row
                last - Grab the last selected item
                index - Returns the index item of the widget.  (Not sure why you would want this, but it's here)

        Return:
            Returns a list of rows that are selected by the user.
        '''
        sort = kwargs.get('sort',False)
        getFirst = kwargs.get('first',False)
        getLast = kwargs.get('last',False)
        indexOnly = kwargs.get('index',False)
        if isinstance(widget,Widgets.QTableView) or isinstance(widget,Widgets.QTableWidget):
            if isinstance(widget,Widgets.QTableWidget):
                if not indexOnly:
                    selection = [str(widget.verticalHeaderItem(index.row()).text())\
                                 for index in widget.selectionModel().selectedRows()]
                else:
                    selection = [index.row() for index in widget.selectionModel().selectedRows()]
            else:
                try:
                    if not indexOnly:
                        selection = [index.row() \
                                     for index in widget.selectionModel().selectedRows()]
                    else:
                        selection = [index.row() for index in widget.selectionModel().selectedRows()]
                except:
                    print('Could not get selection from TableView.  Look at the headerData function there and set orientation and role to named arguments')
                    return []
            if selection:
                if sort:
                    selection = sorted(selection)
                if getFirst:
                    return selection[0]
                elif getLast:
                    return selection[-1]
                else:
                    return selection
        else:
            return []

### Search Bar
    class SearchBar(Widgets.QWidget):
        '''
        Purpose:
                Creates a search bar widget that will search a widget for specific
                strings.  It hides the values that do not fit the criteria

        Input:
                widget - The widget that you want to search.  So far, Listwidgets
                        and ComboBoxes are verified working
                parent - The widget that this will be the child of

        Kwargs:
                regex - True or False.  This will enable or disable regex filtering

        '''
        def __init__(self,widget=None,parent=None,**kwargs):
            super(SearchBar,self).__init__(parent)
            self.parent = parent
            self.widget = widget

            self.addRegex = kwargs.get('regex',True)

            self.GroupRadials = self.makeGroup()

            self.searchLabel = Widgets.QLabel('Search')
            self.searchLine = Widgets.QLineEdit()
            self.searchlayout = Widgets.QGridLayout()
            self.searchlayout.addWidget(self.searchLabel,0,0)
            self.searchlayout.addWidget(self.searchLine,0,1)
            if self.addRegex:
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
            if self.addRegex:
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
        '''
        Creates a list widget that will populate the list with available run
        numbers.

        Input:
                rdir - The directory in which the runs are located.  rfr, tci, etc.
        Kwargs:
                title - Title of the Pop up window
                selection - 0 = single selection
                            1 = multi selection
                            2 = extended selection
                search -    True or False, adds in a search widget to search the items

        return:
                Returns a list of selected items from the list widget, or [].
        '''
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
            print rdir
            runs = glob.glob(os.path.join(rdir,'*[0-9].[0-9]'))
            runs = map(os.path.basename,runs)
            listWidget.addItems(runs)

        retval = widget.exec_()

        # 1 is if Ok is pushed... 0 for cancel or 'X'
        if retval == 1:
            return returnListSelection(listWidget)
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
            
### Simple Yes No Message
    
    def YesNoMessageBox(MessageText,**kwargs):
        '''
        A simple box that asks a question through the Message Text and pops up
        yes or no buttons.  Returns False if 'x' or 'No' clicked, else True if
        'yes' is clicked.
        Input:
            MessageText - The text that you want to show in the box. Should be a yes or no question
        Kwargs:
            title - Changes the title of the window
        Returns:
            True or False
        '''
        title = kwargs.get('title','Select One')
        msg = Widgets.QMessageBox.question(None, title, MessageText, Widgets.QMessageBox.Yes | Widgets.QMessageBox.No, Widgets.QMessageBox.No)
        if msg == Widgets.QMessageBox.Yes:
            return True
        else:
            return False
        
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
### One Offs

    class RadioButtonGroup(Widgets.QGroupBox):
        '''
        This widget belongs in a GUI

        Purpose:
            This will create a group of radio buttons.  That means that only one
            inside the group can be selected at a time.

        Signals:
                buttonChanged - Emits a signal whenever the button in the group has
                                been changed.  This will emit the name of the newly
                                selected radio button.  By default the first button
                                is checked.

        Input:
                buttonNames - A list of button names that you want to be in the group.
                parent  - The widget that this will be the child of

        Kwargs:
                label - A label name for the group.
                        For example, in Phobos I use this for the File,group,dset, and Header
                        search box selection.  So I use label = 'Select Search'
                ori - the orientation you want the buttons to be layed out.
                      "h" = Horizontal
                      "v" = Vertical
                maxperori - The maximum number of things to have based on the orientation
                            For instance, if you set orientation = "h" and maxperori = 4
                            There will be at max 4 items per row, until all items are exhausted.
        '''
        buttonChanged = Core.pyqtSignal(object)
        def __init__(self,buttonNames = [] ,parent=None,**kwargs):
            super(RadioButtonGroup,self).__init__(parent)
            self.n = self.__class__.__name__
            self.parent = parent
            self.buttonNames = buttonNames
            self.labelname = kwargs.get('label','Select Button')
            self.orientation = kwargs.get('ori','h')
            self.maxperori = kwargs.get('maxperori',10000)

            self.makeGroup()
            self.setLayout(self.layout)

        def Emit(self,radiobutton):
            if radiobutton.isChecked():
                self.buttonChanged.emit(radiobutton.text())

        def makeGroup(self):
            self.layout = Widgets.QGridLayout()
            self.Label = Widgets.QLabel(self.labelname)
            self.Label.setSizePolicy(Widgets.QSizePolicy.Expanding, Widgets.QSizePolicy.Expanding)
            self.Label.setAlignment(Core.Qt.AlignCenter)
            if self.orientation.lower() == 'h':
                i = 0
                j = 0
                maxcols = self.maxperori
                for k,name in enumerate(self.buttonNames):
                    if j >= maxcols:
                        i += 1
                        j = 0
                    radiobutton = Widgets.QRadioButton(name)
                    radiobutton.toggled.connect(lambda trash, btn=radiobutton:self.Emit(btn))
                    if k == 0:
                        radiobutton.setChecked(True)
                    self.layout.addWidget(radiobutton,i+1,j)
                    j += 1
            elif self.orientation.lower() == 'v':
                i = 0
                j = 0
                maxrows = self.maxperori
                for k,name in enumerate(self.buttonNames):
                    if i >= maxrows:
                        i = 0
                        j += 1
                    radiobutton = Widgets.QRadioButton(name)
                    radiobutton.toggled.connect(lambda trash, btn=radiobutton:self.Emit(btn))
                    if k == 0:
                        radiobutton.setChecked(True)
                    self.layout.addWidget(radiobutton,i+1,j)
                    i += 1
            colcount = self.layout.columnCount()
            self.layout.addWidget(self.Label,0,0,1,colcount)


class MultipleOpener(Widgets.QDialog):
    '''
    This shit show is for the people who say "Why can't I open multiple files,
    groups, and datasets with PHOBOS?"  Well, here's my take on how it will work.

    This will ask have a series of checkboxes to ask the user what they want to do.
    This UI is complicated AF, so it will be made in QT designer because I don't want
    to go back and forth changing things in this class by hand.
    '''
    #TODO make this use RELLIBPATH
    complete = Core.pyqtSignal(object,object)
    def __init__(self,parent=None,**kwargs):
        super(MultipleOpener,self).__init__(parent)
        pass


class PandasCSVopener(Widgets.QDialog):
    '''
    Purpose:
        To open and preview csv files as opened by Pandas.  Since CSV doesn't
        stand for Comma Separated Values anymore........  This needs to be a thing.
        The table shown, will show how the opened file will look in a dataframe
        with the settings given by the user.  The user can also select the columns
        in which they want to keep in the dataframe.

    Signals:
            complete - Passes the selected Data object as well as all the headers
                       that were available to the user to have been selected.  The
                       second of these is for use in Phobos.

    Input:
            fpath - file path to the .csv file.
            parent - the widget that this dialog will be the child of.  Not necessary to set

    Kwargs:

    '''
    complete = Core.pyqtSignal(object,object)
    def __init__(self,fpath,parent=None,**kwargs):
        super(PandasCSVopener,self).__init__(parent)
        sizeObject = Widgets.QDesktopWidget().screenGeometry(-1)
        self.screenwidth = sizeObject.width()
        self.screenheight = sizeObject.height()
        self.resize(self.screenwidth*(2./3.),self.screenheight*(2./3.))
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
        self.startLabelRow = 3

    def makeConnections(self):
        self.SepSelection.editingFinished.connect(lambda:self.preview())
        self.changeHeaders.toggled.connect(lambda:self.addHeaderWidgets())
        self.addHeaders.toggled.connect(lambda:self.addHeaderWidgets())
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

    def keyPressEvent(self,e):
        e.reject()

    def makeWidget(self):
        self.layout = Widgets.QGridLayout()
        self.SepLabel = Widgets.QLabel('Separator:')
        self.SepSelection = Widgets.QLineEdit(',')
        self.GatherPctLabel = Widgets.QLabel('% data to gather')
        self.GatherPct = Widgets.QLineEdit('100')
        self.GatherPct.setValidator(Gui.QDoubleValidator())
        self.GatherPct.editingFinished.connect(lambda:self.preview())
        self.sortHeaderLabel = Widgets.QLabel('Sorting Label:')
        self.sortHeader = Widgets.QComboBox()
        self.sortHeader.currentIndexChanged.connect(lambda trash:self.preview())
        self.changeHeaders = Widgets.QCheckBox('Change Headers')
        self.addHeaders = Widgets.QCheckBox('Add Headers')
        self.RowNumLabel = Widgets.QLabel('Number of Rows:')
        self.RowNum = Widgets.QLabel('')
        self.previewTable = Widgets.QTableWidget()
        self.previewTable.setEditTriggers(Widgets.QAbstractItemView.NoEditTriggers)
        self.HeadersWidget = Widgets.QWidget()
        self.HeadersWidgetLayout = Widgets.QGridLayout()
        self.HeadersWidget.setLayout(self.HeadersWidgetLayout)
        self.SaveButton = Widgets.QPushButton('Save')
        self.SaveButton.clicked.connect(lambda trash:self.saveOut())
        self.setLayout(self.layout)
        self.layout.addWidget(self.SaveButton,0,0)
        self.layout.addWidget(self.SepLabel,1,0)
        self.layout.addWidget(self.SepSelection,1,1)
        self.layout.addWidget(self.GatherPctLabel,2,0)
        self.layout.addWidget(self.GatherPct,2,1)
        self.layout.addWidget(self.sortHeaderLabel,3,0)
        self.layout.addWidget(self.sortHeader,3,1)
        self.layout.addWidget(self.changeHeaders,4,0)
        self.layout.addWidget(self.addHeaders,4,1)
        self.layout.addWidget(self.RowNumLabel,1000,0)
        self.layout.addWidget(self.RowNum,1000,1)
        colcount = self.layout.columnCount()
        self.layout.addWidget(self.HeadersWidget,5,0,3,colcount)
        self.layout.addWidget(self.previewTable,1001,0,1,colcount)
        self.buttonBox = Widgets.QDialogButtonBox()
        self.buttonBox.setStandardButtons(Widgets.QDialogButtonBox.Ok | Widgets.QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.Accept)
        self.buttonBox.rejected.connect(self.Reject)
        self.layout.addWidget(self.buttonBox,1002,0)

    def addHeaderWidgets(self):
        try:
            for i in range(len(self.newlabel)):
                self.newlabel[i].deleteLater()
                self.origlabel[i].deleteLater()
            self.newlabel = []
            self.origlabel = []
        except:
            pass
        if self.addHeaders.isChecked() or self.changeHeaders.isChecked():
            if self.y.shape[0]:
                self.newlabel = []
                self.origlabel = []
                maxrows = 5
                i = self.startLabelRow
                j = 0
                for k,header in enumerate(list(self.y)):
                    self.origlabel.append(Widgets.QLabel(self.ORIGHEADERS[k]))
                    self.newlabel.append(Widgets.QLineEdit(header))
                    self.newlabel[-1].editingFinished.connect(lambda:self.preview())
                    self.HeadersWidgetLayout.addWidget(self.origlabel[-1],i,j)
                    self.HeadersWidgetLayout.addWidget(self.newlabel[-1],i,j+1)
                    i+=1
                    if i > maxrows+self.startLabelRow:
                        i = self.startLabelRow
                        j+=2

    def preview(self):
        sep = self.SepSelection.text()
        if not sep:
            sep = ' '
        self.ORIGHEADERS = list(pd.read_csv(self.fpath,sep=sep))
        if not self.addHeaders.isChecked() and not self.changeHeaders.isChecked():
            self.y = pd.read_csv(self.fpath,sep=sep)
        elif self.addHeaders.isChecked() and not self.changeHeaders.isChecked():
            self.y = pd.read_csv(self.fpath,sep=sep,names=[header.text() for header in self.newlabel])
        elif self.changeHeaders.isChecked() and not self.addHeaders.isChecked():
            self.y = pd.read_csv(self.fpath,sep=sep).rename(columns={oheader.text():header.text() for oheader,header in zip(self.origlabel,self.newlabel)})
        if self.addHeaders.isChecked():
            minrows = 3
        else:
            minrows = 2
        currSort = self.sortHeader.currentText()
        self.sortHeader.blockSignals(True)
        self.sortHeader.clear()
        items = ['']
        items.extend(list(self.y))
        self.sortHeader.addItems(items)
        if currSort and currSort in self.y:
            self.sortHeader.setCurrentIndex(self.sortHeader.findText(currSort))
        else:
            self.sortHeader.setCurrentIndex(0)
        if self.sortHeader.currentText():
            self.y.sort_values(self.sortHeader.currentText(),inplace=True)
        self.sortHeader.blockSignals(False)
        self.y = self.thinData(self.y,self.GatherPct.text(),minrows=minrows)
        self.allheaders = list(self.y)
        self.RowNum.setText(str(self.y.shape[0]))
        self.addHeaderWidgets()
        self.previewTable.clear()
        self.previewTable.setRowCount(10)
        self.previewTable.setColumnCount(self.y.shape[1])
        self.previewTable.setHorizontalHeaderLabels(list(self.y))
        for row in range (0, self.y.shape[0]):
            for col in range (0, self.y.shape[1]):
                    data = str(self.y.iloc[row, col] )
                    self.previewTable.setItem(row, col, Widgets.QTableWidgetItem(str(data)))

    def thinData(self,array,pct,**kwargs):
        return PF.thin_data(array,pct,**kwargs)

    def saveOut(self,**kwargs):
        sep = self.SepSelection.text()
        if not sep:
            sep = ' '
        if not self.addHeaders.isChecked() and not self.changeHeaders.isChecked():
            self.y = pd.read_csv(self.fpath,sep=sep)
        elif self.addHeaders.isChecked() and not self.changeHeaders.isChecked():
            self.y = pd.read_csv(self.fpath,sep=sep,names=[header.text() for header in self.newlabel])
        elif self.changeHeaders.isChecked() and not self.addHeaders.isChecked():
            self.y = pd.read_csv(self.fpath,sep=sep).rename(columns={oheader.text():header.text() for oheader,header in zip(self.origlabel,self.newlabel)})
        self.y.to_csv(self.fpath,index=False)

    def Accept(self):
        selected = returnTableSelectedColumns(self.previewTable)
        if selected:
            self.y = self.y[selected]
        self.complete.emit(self.y,self.allheaders)
        self.close()

    def Reject(self):
        self.complete.emit(pd.DataFrame(),[])
        self.close()

class RetrieveData(Core.QThread):
    dataRetrieved = Core.pyqtSignal(object)
    queryFinished = Core.pyqtSignal(object)
    def __init__(self,target,args=(),kwargs={},parent=None):
        super(RetrieveData,self).__init__(parent)
        self.target = target
        self.args = args
        self.kwargs = kwargs

    def getThreadId(self):
        return id(self)

    def run(self):
        data = self.target(*self.args,**self.kwargs)
        self.dataRetrieved.emit(data)
        self.queryFinished.emit(self.getThreadId())

    def abort(self):
        self.abort = True
        self.queryFinished.emit(self.getThreadId())


if __name__ == '__main__':
    try:
        app = Widgets.QApplication(sys.argv)
        print 'ahah'
        def showdata(data,headers):
            print(data)
            print(type(data))
            print(data)
            print(headers)
        path = '/home/klinetry/Desktop/Phobos3/Test.csv'
        x = PandasCSVopener(path)
        print 'ahhahs'
        x.complete.connect(showdata)
        print 'sdfsf'
        print 'haha'
        x.show()
        retval = app.exec_()
        sys.exit(retval)
    except:
        pass
