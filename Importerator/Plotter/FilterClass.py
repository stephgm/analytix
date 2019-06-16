# -*- coding: utf-8 -*-
"""
Created on Thu Apr 11 20:36:19 2019

@author: Jordan
"""
from PyQt5.Qt import *
import PyQt5
import pandas as pd

operators = ['Equal To','Less Than','Greater Than','Not Equal To','In Range','Not In Range','Starts With','Does Not Start With','Ends With','Does Not End With','Contains','Does Not Contain','Ascending Order','Descending Order']
orkeys = [str(i) for i in range(10)]
orkeys.insert(0,'')

class FilterClass(object):
    def __init__(self,parent=None,filterwidget=None,**kwargs):
        self.parent = parent
        self.parent.HeaderCombo = []
        self.parent.HeaderOperator = []
        self.parent.UniqueValues = []
        self.parent.FilterOr = []
        self.parent.FilterAnd = []
        self.widget = filterwidget
        self.TableWidget = None
        TRED = '\033[1;30m'
        TRED = ''
        
        #Handle the kwargs
        addheaders = kwargs.pop('clean',True)
        if addheaders not in [True,False]:
            print TRED+'kwarg: clean was not set to True or False, using True as default'
            addheaders = True
        lazyconnect = kwargs.pop('connect',True)
        if lazyconnect not in [True,False]:
            print '\n\n'+TRED+'kwarg: connect was not set to True or False, using True as default.\n'+\
                    "Note: connect = True means that you don't want to do anything special after"\
                    " filtering the table.  If you do, you must make a connection yourself and call"\
                    " the FilterClass 'loadFilters' function in that connection function."\
                    " So add the code 'self.<yourTreeWidgetName>.itemChanged.connect(YourFunc)'"\
                    " and call this class with 'connect=False'."
        self.FirstAdd = lazyconnect
        if lazyconnect:
            print "\n\n"+TRED+"Note: connect = True means that you don't want to do anything special after"\
                    " filtering the table.  If you do, you must make a connection yourself and call"\
                    " the FilterClass 'loadFilters' function in that connection function."\
                    " So add the code 'self.<yourTreeWidgetName>.itemChanged.connect(YourFunc)'"\
                    " and call this class with 'connect=False'."
        
        if not isinstance(self.widget,PyQt5.QtWidgets.QTreeWidget):
            print '\n\n'+TRED+'Your Filter widget was not a Tree Widget, I will take care of that for you.'\
                'NOTE: This feature does not work at the moment.  I dont know how to tranform widgets, '\
                'so just make sure your filter widget is a TreeWidget.'\
                ' For the moment, this will change it to a treewidget but will not display anything in your current widget.'
            filterwidget = QTreeWidget()
            self.widget = filterwidget
            addheaders = True
        
        
        if addheaders:
            header=QTreeWidgetItem(['State','Header','Operator','Value','Or Check','And Check'])
            self.widget.setHeaderItem(header)
        

    def addFilters(self,tablewidget,filterlist,headers):
#        if self.TableWidget != tablewidget:
#            self.FirstAdd = True
#        if self.FirstAdd:
#            self.TableWidget = tablewidget
#            self.widget.itemChanged.connect(lambda:self.loadFilters(tablewidget,filterlist,headers))
#            self.FirstAdd = False
        headers = headers
        item = QTreeWidgetItem()
        item.setFlags(item.flags() | Qt.ItemIsSelectable | Qt.ItemIsUserCheckable | Qt.ItemIsEditable)
        self.parent.HeaderCombo.append(QComboBox())
        self.parent.HeaderOperator.append(QComboBox())
        self.parent.FilterOr.append(QComboBox())
        self.parent.FilterAnd.append(QComboBox())
        self.parent.UniqueValues.append(QComboBox())
        self.parent.HeaderCombo[-1].addItems(headers)
        self.parent.HeaderOperator[-1].addItems(operators)
        self.parent.FilterOr[-1].addItems(orkeys)
        self.parent.FilterAnd[-1].addItems(orkeys)
        item.setText(3,'')
        item.setCheckState(0,Qt.Checked)
        self.parent.HeaderCombo[-1].activated.connect(lambda:self.uniqueValues(tablewidget,filterlist,headers))
        self.parent.HeaderOperator[-1].activated.connect(lambda:self.loadFilters(tablewidget,filterlist,headers))
        self.parent.FilterOr[-1].activated.connect(lambda:self.loadFilters(tablewidget,filterlist,headers))
        self.parent.FilterAnd[-1].activated.connect(lambda:self.loadFilters(tablewidget,filterlist,headers))
        self.parent.UniqueValues[-1].activated.connect(lambda:self.loadFilters(tablewidget,filterlist,headers))
        self.parent.HeaderCombo[-1].setCurrentIndex(0)
        self.parent.HeaderOperator[-1].setCurrentIndex(0)
        self.parent.FilterOr[-1].setCurrentIndex(-1)
        self.parent.FilterAnd[-1].setCurrentIndex(-1)
        self.widget.addTopLevelItem(item)
        if tablewidget.model().getDtype(headers[0]) == 'O':
            vals = tablewidget.model().getColumnData(headers[0])
            self.parent.UniqueValues[-1].addItems(pd.unique(vals))
            self.widget.setItemWidget(item,3,self.parent.UniqueValues[-1])
        self.widget.setItemWidget(item,1,self.parent.HeaderCombo[-1])
        self.widget.setItemWidget(item,2,self.parent.HeaderOperator[-1])
        self.widget.setItemWidget(item,4,self.parent.FilterOr[-1])
        self.widget.setItemWidget(item,5,self.parent.FilterAnd[-1])
        filterlist.append([self.parent.HeaderCombo[-1].currentText(),self.parent.HeaderOperator[-1].currentText(),item.text(3),0,self.parent.FilterOr[-1].currentText(),self.parent.FilterAnd[-1].currentText()])
                
    def loadFilters(self,tablewidget,filterlist,headers):
        procedures = []
        headers = headers
        
        for i in range(self.widget.topLevelItemCount()):
            item = self.widget.topLevelItem(i)
            filterlist[i][0] = self.parent.HeaderCombo[i].currentText()
            filterlist[i][1] = self.parent.HeaderOperator[i].currentText()
            if tablewidget.model().getDtype(self.parent.HeaderCombo[i].currentText()) == 'O':
                filterlist[i][2] = self.parent.UniqueValues[-1].currentText()
            else:
                filterlist[i][2] = item.text(3)
            filterlist[i][4] = self.parent.FilterOr[i].currentText()
            filterlist[i][5] = self.parent.FilterAnd[i].currentText()
            if item.checkState(0) == Qt.Checked:
                filterlist[i][3] = 1
                procedures.append([filterlist[i][0],filterlist[i][1],filterlist[i][2],filterlist[i][4],filterlist[i][5]])
            else:
                filterlist[i][3] = 0
        tablewidget.model().filterTable(procedures)
            
    def addFilterTree(self,tablewidget,filterlist,headers):
        self.widget.clear()
        self.parent.HeaderCombo = []
        self.parent.HeaderOperator = []
        self.parent.FilterOr = []
        self.parent.FilterAnd = []
        filts = filterlist
        headers = headers
        for filt in filts:
            if filt[0] not in headers:
                continue
            item = QTreeWidgetItem()
            item.setFlags(item.flags() | Qt.ItemIsSelectable | Qt.ItemIsUserCheckable | Qt.ItemIsEditable)
            self.parent.HeaderCombo.append(QComboBox())
            self.parent.HeaderOperator.append(QComboBox())
            self.parent.FilterOr.append(QComboBox())
            self.parent.FilterAnd.append(QComboBox())
            self.parent.UniqueValues.append(QComboBox())
            self.parent.HeaderCombo[-1].addItems(headers)
            self.parent.HeaderOperator[-1].addItems(operators)
            self.parent.FilterOr[-1].addItems(orkeys)         
            self.parent.FilterAnd[-1].addItems(orkeys)
            item.setText(3,filt[2])
            if filt[3] == 1:
                item.setCheckState(0,Qt.Checked)
            else:
                item.setCheckState(0,Qt.Unchecked)
            self.parent.HeaderCombo[-1].activated.connect(lambda:self.uniqueValues(tablewidget,filterlist,headers))
            self.parent.HeaderOperator[-1].activated.connect(lambda:self.loadFilters(tablewidget,filterlist,headers))
            self.parent.FilterOr[-1].activated.connect(lambda:self.loadFilters(tablewidget,filterlist,headers))
            self.parent.FilterAnd[-1].activated.connect(lambda:self.loadFilters(tablewidget,filterlist,headers))
            self.parent.UniqueValues[-1].activated.connect(lambda:self.loadFilters(tablewidget,filterlist,headers))
            index = self.parent.HeaderCombo[-1].findText(filt[0])
            self.parent.HeaderCombo[-1].setCurrentIndex(index)
            index = self.parent.HeaderOperator[-1].findText(filt[1])
            self.parent.HeaderOperator[-1].setCurrentIndex(index)
            index = self.parent.FilterOr[-1].findText(filt[4])
            self.parent.FilterOr[-1].setCurrentIndex(index)
            index = self.parent.FilterAnd[-1].findText(filt[5])
            self.parent.FilterAnd[-1].setCurrentIndex(index)
            if tablewidget.model().getDtype(headers[0]) == 'O':
                vals = tablewidget.model().getColumnData(headers[0])
                self.parent.UniqueValues[-1].addItems(pd.unique(vals))
                index = self.parent.UniqueValues[-1].findText(filt[4])
                self.parent.UniqueValues[-1].setCurrentIndex(index)
                self.widget.setItemWidget(item,3,self.UniqueValues[-1])
            self.widget.addTopLevelItem(item)
            self.widget.setItemWidget(item,1,self.parent.HeaderCombo[-1])
            self.widget.setItemWidget(item,2,self.parent.HeaderOperator[-1])
            self.widget.setItemWidget(item,4,self.parent.FilterOr[-1])
            self.widget.setItemWidget(item,5,self.parent.FilterAnd[-1])
        self.loadFilters(tablewidget,filterlist,headers)
            
    def uniqueValues(self,tablewidget,filterlist,headers):
        for i in range(self.widget.topLevelItemCount()):
            item = self.widget.topLevelItem(i)
            if tablewidget.model().getDtype(self.parent.HeaderCombo[i].currentText()) == 'O':
                vals = tablewidget.model().getColumnData(self.parent.HeaderCombo[i].currentText())
                self.parent.UniqueValues[i] = QComboBox()
                self.parent.UniqueValues[i].addItems(pd.unique(vals))
                self.parent.FilterTree.setItemWidget(item,3,self.parent.UniqueValues[i])
                item.setText(3,'')
            else:
                try:
                    txt = item.text(3)
                except:
                    txt = ''
                self.parent.UniqueValues[i].clear()
                self.widget.removeItemWidget(item,3)
                item.setText(3,txt)
        self.loadFilters(tablewidget,filterlist,headers)