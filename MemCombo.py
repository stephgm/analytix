#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 16 18:32:20 2019

@author: klinetry
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
from collections.abc import Iterable
import psutil


class MemoryManager(Widgets.QWidget):
    Terminate = Core.pyqtSignal(object)
    def __init__(self,parent=None,**kwargs):
        '''
        Purpose:
                This is a widget that is a simple combo box that will
                have a selection of percentages and memory in GB.  Whatever the
                selection is set on, the widget will check the current memory usage
                whenever the function checkMemory is called.  This will return
                a bool whether the current memory usage is over the threshold set
                or not.  This can also be used without creating a widget by setting
                the makeWidget kwarg = False

        Input:
                parent - The parent of this widget

        Kwargs:
                makeWidget - True or False.  Use a widget or just a class
                alertpct - The percent you want to set as the cutoff initially.
                useTimer - Makes a Qtimer to check memory every 10 seconds.
                            Could be faulty. Not sure how Qtimers work with
                            things that are processing.

        Signals:
                Terminate - Will emit a True signal if you should raise a memory error
        '''
        super(MemoryManager,self).__init__(parent)

        self.makeWidget = kwargs.get('makeWidget',True)
        self.AlertPercent = kwargs.get('alertpct',90)
        self.useTimer = kwargs.get('useTimer',False)
        if self.useTimer:
            self.timer = Core.QTimer()
            self.timer.timeout.connect(self.checkMemory)
            self.timer.start(10000) #10 seconds

        self.MaxMemory = psutil.virtual_memory()[0]/float(1024**3)
        if self.AlertPercent % 5 != 0:
            # Ensures that AlertPercent is a multiple of 5 so that it will be in the
            # combo box.  Always rounds down for safety
            self.AlertPercent -= self.AlertPercent%5

        if self.makeWidget:
            self.createWidget()
        self.setKillPct()

    def createWidget(self,**kwargs):
        self.layout = Widgets.QGridLayout()
        self.MemoryCombo = Widgets.QComboBox()
        self.MemoryCombo.addItems(['{}% = {} GB'.format(percent,self.MaxMemory*percent*.01) for percent in range(90,0,-5)])
        index = self.MemoryCombo.findText('{}% = {} GB'.format(self.AlertPercent,self.MaxMemory*self.AlertPercent*.01))
        if index > 0:
            self.MemoryCombo.setCurrentIndex(index)
        else:
            self.MemoryCombo.setCurrentIndex(0)
        self.MemoryCombo.currentIndexChanged.connect(lambda trash: self.setKillPct())
        self.layout.addWidget(self.MemoryCombo)
        self.setLayout(self.layout)

    def setKillPct(self,**kwargs):
        if self.makeWidget:
            self.AlertPercent = int(self.MemoryCombo.currentText().split('%')[0])
            self.checkMemory()

    def checkMemory(self,**kwargs):
        if self.useTimer:
            self.timer.start(10000)
        currpct = psutil.virtual_memory()[2]
        if isinstance(self.AlertPercent,int):
            try:
                self.AlertPercent = int(self.AlertPercent)
            except:
                self.AlertPercent = 90
        if currpct >= self.AlertPercent:
            self.Terminate.emit(True)
            return True
        else:
            return False

if __name__ == '__main__':
    app = Widgets.QApplication(sys.argv)
    def showdata(data):
        print(data)
    x = MemoryManager(None,alertpct=83)
    x.Terminate.connect(showdata)
    x.show()
    retval = app.exec_()
    sys.exit(retval)
