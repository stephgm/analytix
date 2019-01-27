#!/usr/bin/env python
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
import h5py
LIBPATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
#print("LIBPATH : "+LIBPATH)
sys.path.extend([_ for _ in glob.glob(os.path.join(LIBPATH,'*'))
                 if os.path.isdir(_)])
import utils
#with h5py.File('idap.h5','r') as hh:
#    data = hh['/ota.acquisitionSummary'][...]
#utils.csvWriter(data,'idap.csv')
#x = utils.csvReaderLargeAdar('idap.csv',['protocol','timeRvTrack','sensorName'])
#print(x)
#utils.csvWriter(x,'idap_r.csv')
#sys.exit()
class AdarConfigurator(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)),'adarConfigurator.ui'), self)
        self.setWindowTitle("AEGIS ADAR Version Configurator")
        self.filebasename = 'aegisVersionConfig.ini'
        self.data = {}
        self.versions = ['','4.0.3','4.1.0','5.0','BL9.B1','BL9.B2','BL9.C1','BL0.C2']
        self.makeConnections()
    def makeConnections(self):
        self.selectExecutionPath.clicked.connect(lambda x:self.selectPath(self.ExecutionPath))
        #self.selectExecutionPath.clicked.connect(self.selectPath(self.ExecutionPath))
        self.ExecutionPath.editingFinished.connect(self.populateRunBox)
        self.ExecutionPath.textChanged.connect(self.populateRunBox)
        #self.runListBox.itemSelectionChanged.connect(self.populateElementBox)
        self.runListBox.itemClicked.connect(self.populateElementBox)
        self.elementListBox.itemClicked.connect(self.getVersionInfo)
        self.versionComboBox.addItems(self.versions)
        self.versionComboBox.currentIndexChanged.connect(self.setVersionInfo)
    def selectPath(self,widget):
        spath = QFileDialog.getExistingDirectory()
        if spath:
            widget.setText(spath)
    def populateRunBox(self):
        self.data = utils.read_ini(os.path.join(str(self.ExecutionPath.text()),self.filebasename))
        self.runListBox.blockSignals(True)
        self.elementListBox.blockSignals(True)
        self.versionComboBox.blockSignals(True)
        self.versionComboBox.setCurrentIndex(0)
        self.elementListBox.clear()
        self.runListBox.clear()
        for indir in glob.glob(os.path.join(str(self.ExecutionPath.text()),'*')):
            if os.path.isdir(indir):
                rr = os.path.basename(indir)
                self.runListBox.addItem(rr)
                if rr not in self.data:
                    self.data[rr] = {}
                for ab in glob.glob(os.path.join(indir,'ELEMENT','AEGIS_*')):
                    abn = os.path.basename(ab)
                    if abn not in self.data[rr]:
                        self.data[rr][abn] = ['']
        self.runListBox.blockSignals(False)
        self.elementListBox.blockSignals(False)
        self.versionComboBox.blockSignals(False)
    def getVersionInfo(self):
        rr = self.runListBox.currentItem().text()
        abn = self.elementListBox.currentItem().text()
        self.versionComboBox.setCurrentIndex(self.versionComboBox.findText(self.data[rr][abn][0]))
        #print(self.versionComboBox.currentText())
    def setVersionInfo(self):
        rr = self.runListBox.currentItem()
        abn = self.elementListBox.currentItem()
        if rr and abn:
            rr = rr.text()
            abn = abn.text()
            vers = self.versionComboBox.currentText()
            self.data[rr][abn] = [vers]
    def populateElementBox(self,item):
        self.elementListBox.blockSignals(True)
        self.versionComboBox.blockSignals(True)
        self.versionComboBox.setCurrentIndex(0)
        self.elementListBox.clear()
        rr = item.text()
        for ele in self.data[rr]:
            self.elementListBox.addItem(ele)
        self.elementListBox.blockSignals(False)
        self.versionComboBox.blockSignals(False)
    def closeEvent(self,event):
        ep = str(self.ExecutionPath.text())
        if ep and os.path.isdir(ep):
            utils.write_ini(self.data,os.path.join(ep,self.filebasename))

def main():
    app = QApplication(sys.argv)
    frame = AdarConfigurator()
    frame.show()
    retval = app.exec_()
    sys.exit(retval)

if __name__ == '__main__':
    main()