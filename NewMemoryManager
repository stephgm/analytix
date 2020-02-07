#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 16 18:32:20 2019

@author: Carl
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
import psutil
import sched
import time
import threading
import numpy
import zmq
import multiprocessing


class MemManager(threading.Thread):
    def __init__(self,parentPID,**kwargs):
        super(MemManager, self).__init__()
        self._stop_event = threading.Event()
        self.AlertPercent = kwargs.get('alertpct',90)
        self.checkTime = kwargs.get('checkTime',10)
        self.parentPID = parentPID
        self.setDaemon(True)
        self.start()
    
    def stop(self):
        self._stop_event.set()

    def join(self, *args, **kwargs):
        self.stop()
        super(MemManager,self).join(*args, **kwargs)

    def run(self):
        while not self._stop_event.is_set():
            self.checkMemory()
            time.sleep(self.checkTime)
        
    def checkMemory(self,**kwargs):
        currpct = psutil.virtual_memory()[2]
        if isinstance(self.AlertPercent,int):
            try:
                self.AlertPercent = int(self.AlertPercent)
            except:
                self.AlertPercent = 90
        sys.stdout.flush()
        if currpct >= self.AlertPercent:
            if self.parentPID != None:
                try:
                    self.genocide()
                except:
                    print('Cannot perform a genocidal act to the parent and the children.  Thats a shame.')

    def genocide(self,**kwargs):
        print('dropping the nuke')
        parent = psutil.Process(self.parentPID)
        for child in parent.children(recursive=True):
            print(child)# or parent.children() for recursive=False
            child.kill()
        print('everything should be dead')
        sys.stdout.flush()
        parent.kill()

def fuckItUp():
    print('childPID',os.getpid())
    import sys
    #sys.stdout.flush()
    import numpy as np
    x = pd.DataFrame(index = range(1000000),columns=['a','b','c','d','e'])
    a = numpy.empty(1000000)
    y = pd.DataFrame()
    thislist = []
    for i in range(100000):
        print(3)
        y = pd.concat([y,x])
        thislist.append(a.copy())
#        import time
#        time.sleep(10)

if __name__ == '__main__':
    app = Widgets.QApplication(sys.argv)

    #Performing Hamilton Laptop melting test.
    import os
    parentPID = os.getpid()
    import multiprocessing
    from multiprocessing import Process
    print(parentPID)

    # p = Process(target=MemManager,args=(parentPID,),kwargs={'checkTime':2,'alertpct':50})
    # p.start()
    p = MemManager(parentPID, alertpct=60,checkTime=2)

    procs = []
    for i in range(2):
        proc = Process(target=fuckItUp)
        procs.append(proc)
        proc.start()
    for proc in procs:
        proc.join()
    print('done son')
    sys.exit(0)
