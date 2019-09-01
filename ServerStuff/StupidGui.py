#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 30 18:54:54 2019

@author: klinetry
"""
from PyQt5.Qt import *
#from PyQt5 import QtSql
#from PyQt5.QtCore import QVariant
from PyQt5 import uic
import sys
import os
import zmq
import time

import ZMQGenericClient

class Gui(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        uic.loadUi('stupidgui.ui', self)

        self.client = ZMQGenericClient.GenericClient(self)

        self.makeConnections()

    def makeConnections(self):
        self.shutdownbtn.clicked.connect(lambda trash:self.shutdownserver())
        self.pushbtn.clicked.connect(lambda trash:self.sendPush())
        self.disconnectbtn.clicked.connect(lambda trash:self.disconnect())
        self.reconnectbtn.clicked.connect(lambda trash:self.reconnect())
        self.getData.clicked.connect(lambda trash:self.getfile())

    def getfile(self):
        self.client.send({'type':'requestfilefromrun','message':'test:561:marlow.h5:ota.acquisitionSummary::'})

    def getdata(self):
        self.client.send({'type':'test'})

    def disconnect(self):
        if self.client.connected:
            self.shutdownbtn.setEnabled(False)
            self.pushbtn.setEnabled(False)
            self.client.stopThreads()

    def reconnect(self):
        print self.client.connected
        if not self.client.connected:
            print 'in here'
            self.client.connect()
            self.shutdownbtn.setEnabled(True)
            self.pushbtn.setEnabled(True)

    def sendPush(self):
        self.setEnabled(False)
        self.client.send({'type':'push','message':'','data':[1,2,3,4]})
        self.setEnabled(True)
    def shutdownserver(self):
        self.client.send({'type':'shutdown','message':'20'})

    def Alert(self,msg):
        self.statusbar.showMessage(msg)

    def handleDisconnect(self):
        pass

    def addDatatoTable(self,data):

        self.TableWidget.setRowCount(data.shape[0])
        self.TableWidget.setColumnCount(data.shape[1])
        for rownum,header in enumerate(list(data)):
            for colnum in range(data.shape[1]):
                self.TableWidget.setItem(rownum,colnum,QTableWidgetItem(str(data[header][colnum])))

    def closeEvent(self,event):
        if self.client.connected:
            self.client.send({'type':'Disconnect'})
            self.client.stopThreads()
            print 'successfully stopped the threads'
        event.accept()
        self.close()
#        self.client.stopListening()
#        event.accept()
#        self.close()

def main():
    app = QApplication(sys.argv)
    frame = Gui()
    frame.show()
#    splash.finish(frame)
    retval = app.exec_()
    sys.exit(retval)


if __name__ == '__main__':
    main()