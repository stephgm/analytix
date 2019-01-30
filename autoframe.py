#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Sun Jan  7 15:04:18 2018

@author: hollidayh
"""
import sys
from PyQt4.QtGui  import *
from PyQt4.QtCore import *

class MyAutoTab(QWidget):
    def __init__(self,parent=None):
        QWidget.__init__(self)
        self.main_frame = QWidget()
        lvbox = QVBoxLayout()
        rvbox = QVBoxLayout()
        hbox  = QHBoxLayout()
        self._models = []
        self.setWindowTitle("Auto Framing Example")
        self.resize(400, 800)
        self.tabWidget = QTabWidget()
        for ele in ('GMD','THAAD'):
            tab = QWidget()
            listView = QListView()
            self._models.append(QStandardItemModel())
            thisLayout = QVBoxLayout()
            for itemn in ('plotThis','plotThat'):
                item = QStandardItem(itemn+ele)
                item.setCheckState(Qt.Unchecked)
                item.setCheckable(True)
                self._models[-1].appendRow(item)
            listView.setModel(self._models[-1])
            thisLayout.addWidget(listView)
            tab.setLayout(thisLayout)
            self.tabWidget.addTab(tab,ele)
        lvbox.addWidget(self.tabWidget)
        self.printWidgets = QPushButton("Print Widgets")
        self.printWidgets.clicked.connect(self.printWidgetFunc)
        lvbox.addWidget(self.printWidgets)
        # ===================
        self.initializeButton = QPushButton("Initialize")
        self.initializeButton.setFixedHeight(50)
        self.initializeButton.setFixedWidth(100)
        self.executeButton = QPushButton("Execute")
        self.newMissionButton = QPushButton("NewMission")
        rvbox.addWidget(self.initializeButton)
        rvbox.addWidget(self.executeButton)
        rvbox.addWidget(self.newMissionButton)
        hbox.addLayout(lvbox)
        hbox.addLayout(rvbox)
        self.setLayout(hbox)
    def printWidgetFunc(self):
        for model in self._models:
            for row in range(model.rowCount()):
                model_index = model.index(row, 0)
                name = str(model.data(model_index).toString())
                if model.data(model_index,Qt.CheckStateRole) == Qt.Checked:
                    print(name)
if __name__ == "__main__":
    app = QApplication([])
    form = MyAutoTab()
    form.show()
    sys.exit(app.exec_())