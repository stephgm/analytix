#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 25 20:07:06 2019

@author: hollidayh
"""
import sys
import os
import glob
from PyQt5 import *
from PyQt5.Qt import *
from PyQt5 import uic

class AdarConfigurator(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        uic.loadUi('adarConfigurator.ui', self)
        self.makeConnections()
    def makeConnections(self):
        self.selectExecutionPath.clicked.connect(lambda x:self.selectPath(self.ExecutionPath))
        #self.selectExecutionPath.clicked.connect(self.selectPath(self.ExecutionPath))
        self.ExecutionPath.editingFinished.connect(self.populateRunBox)
        self.ExecutionPath.textChanged.connect(self.populateRunBox)
    def selectPath(self,widget):
        spath = QFileDialog.getExistingDirectory()
        if spath:
            widget.setText(spath)
    def populateRunBox(self):
        self.runListBox.blockSignals(True)
        self.runListBox.clear()
        for indir in glob.glob(os.path.join(str(self.ExecutionPath.text()),'*')):
            if os.path.isdir(indir):
                self.runListBox.addItem(os.path.basename(indir))
        self.runListBox.blockSignals(False)

def main():
    app = QApplication(sys.argv)
    frame = AdarConfigurator()
    frame.show()
    retval = app.exec_()
    sys.exit(retval)

if __name__ == '__main__':
    main()