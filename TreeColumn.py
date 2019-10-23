#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 22 19:06:23 2019

@author: Jordan
"""
import sys
import PyQt5.QtWidgets as Widgets
import PyQt5.QtGui as Gui
import PyQt5.QtCore as Core
import PyQt5.uic as Qt5
import pandas as pd
import time

class StringTreeColumn(Widgets.QTreeWidget):
    def __init__(self,parent=None,headers=[],**kwargs):
        super(StringTreeColumn,self).__init__(parent)
        self.parent = parent
        self.headers = headers

        self.addChecks = kwargs.get('addChecks',False)
        self.initialCheckState = kwargs.get('initCheckState',False)
        self.editable = kwargs.get('editable',False)

        self.headermap = {k:v for v,k in enumerate(self.headers)}
        if not self.headermap:
            print('You are passing no headers, you should probably just use a list widget')
            return
        if self.headers:
            self.setHeaderItem(Widgets.QTreeWidgetItem(self.headers))

    def addItems(self,ItemDict):
        if not isinstance(ItemDict,dict):
            return
        Items = pd.DataFrame(ItemDict)
        if not set(self.headers).issubset(set(list(Items))):
            return
        Items = Items[self.headers]
        for i in range(Items.shape[0]):
            item = Widgets.QTreeWidgetItem()
            item.setFlags(item.flags() | Core.Qt.ItemIsSelectable)
            if self.addChecks:
                item.setFlags(item.flags() | Core.Qt.ItemIsUserCheckable)
            if self.editable:
                item.setFlags(item.flags() | Core.Qt.ItemIsEditable)
            for field in Items:
                item.setText(self.headermap[field],str(Items[field][i]))
            if self.addChecks:
                if self.initialCheckState:
                    item.setCheckState(0,Core.Qt.Checked)
                else:
                    item.setCheckState(0,Core.Qt.Unchecked)
            self.addTopLevelItem(item)

    def removeItems(self,indecies):
        itemsToRemove = []
        if indecies:
            for index in indecies:
                item=self.topLevelItem(index)
                if item:
                    itemsToRemove.append(item)
            for item in itemsToRemove:
                for i in range(self.topLevelItemCount()):
                    listItem=self.topLevelItem(i)
                    if not listItem:
                        continue
                    if not listItem in itemsToRemove:
                        continue
                    if item == listItem:
                        self.takeTopLevelItem(i)

    def returnCheckedItems(self):
        indecies = []
        if self.addChecks:
            for i in range(self.topLevelItemCount()):
                item = self.topLevelItem(i)
                if item.checkState(0) == Core.Qt.Checked:
                    indecies.append(i)
        return indecies


if __name__ == '__main__':
#    try:
        app = Widgets.QApplication(sys.argv)
        x = StringTreeColumn(None,['This','That'],addChecks=True,initCheckState=True)
        x.addItems({'This':[1,2,3],'That':['f','ghoo','goood']})
        x.show()
        checked = x.returnCheckedItems()
        time.sleep(5)
        x.removeItems([0,1,2])
        retval = app.exec_()
        sys.exit(retval)
#    except:
#        pass
