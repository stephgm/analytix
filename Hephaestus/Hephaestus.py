#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 24 18:45:32 2020

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
from six import string_types
import json


def popUpSimpleText(MessageText,initstring='',**kwargs):
    title = kwargs.get('title','Enter some text')
    text, okPressed = Widgets.QInputDialog.getText(None, title,MessageText,Widgets.QLineEdit.Normal, initstring)
    if okPressed and text != '':
        return text
    else:
        return ''

os.environ['TOOLS_CONFIG_DIR'] = os.path.join(os.path.expanduser('~'),'Desktop')

class Hephaestus(Widgets.QMainWindow):
    def __init__(self, parent=None):
        Widgets.QMainWindow.__init__(self, parent)
        Qt5.loadUi('Hephaestus.ui', self)
        
        
        self.re_init()
        self.read_json_file()
        self.makeConnections()
        
    def read_json_file(self):
        self.fpath = os.path.join(os.environ['TOOLS_CONFIG_DIR'],'EventConfig.json')
        if os.path.isfile(self.fpath):
            with open(self.fpath,'r') as jf:
                self.data = json.load(jf)
        else:
            with open(self.fpath,'w') as jf:
                json.dump({},jf)
            self.data = {}
        if 'Ground Test' in self.data:
            self.DomainTypeCombo.setCurrentIndex(0)
        elif 'Generic' in self.data:
            self.DomainTypeCombo.setCurrentIndex(1)
        
        self.populate_domains()
        self.populate_events()
        self.check_domain_event()
        
    def makeConnections(self):
        #Global Connections
        self.DomainTypeCombo.currentIndexChanged.connect(lambda trash:self.populate_domains())
        self.DomainCombo.currentIndexChanged.connect(lambda trash:self.populate_events())
        self.EventCombo.currentIndexChanged.connect(lambda trash:self.populate_paths())
        self.DomainTypeCombo.currentIndexChanged.connect(lambda trash:self.check_domain_event())
        self.DomainCombo.currentIndexChanged.connect(lambda trash:self.check_domain_event())
        self.EventCombo.currentIndexChanged.connect(lambda trash:self.check_domain_event())
        
        self.NewDomainButton.clicked.connect(lambda trash:self.add_new_domain())
        self.NewEventButton.clicked.connect(lambda trash:self.add_new_event())
        self.SaveButton.clicked.connect(lambda trash:self.save_json())
        
        #For Ground Test
        self.EventBaseLine.textChanged.connect(lambda trash:self.fill_ground_paths())
        self.EventBaseWindowsLine.textChanged.connect(lambda trash:self.fill_ground_paths())
        
        for line in self.ground_test_dict:
            line.textChanged.connect(lambda trash,line=line:self.update_ground_test_dict(line))
        self.AddPhase.clicked.connect(lambda trash:self.add_ground_test_phase())
        self.RemovePhases.clicked.connect(lambda trash:self.remove_ground_test_phases())
        self.AutoPopulate.clicked.connect(lambda trash:self.ground_test_autopopulate())
        
        self.EventBaseButton.clicked.connect(lambda trash:self.get_ground_Dir(self.EventBaseLine))
        self.EventBaseWindowsButton.clicked.connect(lambda trash:self.get_ground_Dir(self.EventBaseWindowsLine))
        self.ConfigButton.clicked.connect(lambda trash:self.get_ground_Dir(self.ConfigLine))
        self.ExecButton.clicked.connect(lambda trash:self.get_ground_Dir(self.ExecLine))
        self.OutputButton.clicked.connect(lambda trash:self.get_ground_Dir(self.OutputLine))
        self.DoxButton.clicked.connect(lambda trash:self.get_ground_Dir(self.DoxLine))
        self.DataButton.clicked.connect(lambda trash:self.get_ground_Dir(self.DataLine))
        self.OSFButton.clicked.connect(lambda trash:self.get_ground_Dir(self.OSFLine))
        self.ITPButton.clicked.connect(lambda trash:self.get_ground_Dir(self.ITPLine))
        
        #For Generic
        self.AddDataPathButton.clicked.connect(lambda trash:self.add_generic_test_phase())
        self.RemoveDataPathsButton.clicked.connect(lambda trash:self.remove_generic_test_phases())
        
        self.GenEventButton.clicked.connect(lambda trash:self.get_generic_Dir(self.GenericEventLine))
        self.GenEventButtonWindows.clicked.connect(lambda trash:self.get_generic_Dir(self.GenericEventLineWindows))
        # self.GenExecButton.clicked.connect(lambda trash:self.get_generic_Dir(self.GenericExecLine))
        
        # self.GenericExecLine.textChanged.connect(lambda trash:self.update_generic_Data())
        
        
        
    def re_init(self):
        self.ground_test_dict={self.ConfigLine:'',
                               self.ExecLine:'',
                               self.OutputLine:'',
                               self.DoxLine:'',
                               self.DataLine:'',
                               self.OSFLine:'',
                               self.ITPLine:''}
        self.ground_test_names={self.ConfigLine:'config',
                                self.ExecLine:'execution',
                                self.OutputLine:'output',
                                self.DoxLine:'documentation',
                                self.DataLine:'data',
                                self.OSFLine:'osf',
                                self.ITPLine:'itp'}
        
        
        qlines = self.findChildren(Widgets.QLineEdit)
        for line in qlines:
            line.clear()
        qtrees = self.findChildren(Widgets.QTreeWidget)
        for tree in qtrees:
            tree.clear()
            
        self.ComboList = []
        
    def check_domain_event(self):
        if self.DomainCombo.currentText() and self.EventCombo.currentText():
            enable = True
        else:
            enable = False
        qlines = self.findChildren(Widgets.QLineEdit)
        qtrees = self.findChildren(Widgets.QTreeWidget)
        for line in qlines:
            line.setEnabled(enable)
        for tree in qtrees:
            tree.setEnabled(enable)
    
    def add_new_domain(self):
        domain = popUpSimpleText('Domain Name:', title='Enter Domain')
        if domain:
            self.DomainCombo.addItem(domain)
            index = self.DomainCombo.findText(domain)
            self.DomainCombo.setCurrentIndex(index)
            
    def add_new_event(self):
        if self.DomainCombo.currentText():
            event = popUpSimpleText('Event Name:', title = 'Enter Event')
            if event:
                self.EventCombo.addItem(event)
                index = self.EventCombo.findText(event)
                self.EventCombo.setCurrentIndex(index)
                
    def populate_domains(self):
        self.DomainCombo.blockSignals(True)
        self.EventCombo.blockSignals(True)
        self.DomainCombo.clear()
        self.EventCombo.clear()
        self.re_init()
        domaintype = self.DomainTypeCombo.currentText()
        if domaintype in self.data:
            for domain in self.data[domaintype]:
                self.DomainCombo.addItem(domain)
            self.DomainCombo.setCurrentIndex(0)
        self.DomainCombo.blockSignals(False)
        self.EventCombo.blockSignals(False)
        self.populate_events()
        
    def populate_events(self):
        self.EventCombo.blockSignals(True)
        self.EventCombo.clear()
        self.re_init()
        domaintype = self.DomainTypeCombo.currentText()
        domain = self.DomainCombo.currentText()
        for i in range(self.DomainCombo.count()):
            text = self.DomainCombo.itemText(i)
            if domain != text and (domaintype not in self.data or text not in self.data[domaintype]):
                self.DomainCombo.removeItem(i)
        
        if domaintype in self.data and domain in self.data[domaintype]:
            for event in self.data[domaintype][domain]:
                self.EventCombo.addItem(event)
            self.EventCombo.setCurrentIndex(0)
            if self.EventCombo.currentText():
                self.populate_paths()
        self.EventCombo.blockSignals(False)
                
    def populate_paths(self):
        domaintype = self.DomainTypeCombo.currentText()
        domain = self.DomainCombo.currentText()
        eventName = self.EventCombo.currentText()
        self.re_init()
        for i in range(self.EventCombo.count()):
            text = self.EventCombo.itemText(i)
            if eventName != text and (domaintype not in self.data or domain not in self.data[domaintype] or text not in self.data[domaintype][domain]):
                self.EventCombo.removeItem(i)
        if os.name == 'posix':
            index = 0
        else:
            index = 1
        if domaintype in self.data and domain in self.data[domaintype] and eventName in self.data[domaintype][domain]:
            if domaintype == 'Ground Test':
                linuxeventBase = self.data[domaintype][domain][eventName]['Base'][0]
                windowseventBase = self.data[domaintype][domain][eventName]['Base'][1]
                self.EventBaseLine.setText(linuxeventBase)
                self.EventBaseWindowsLine.setText(windowseventBase)
                for tl in self.data[domaintype][domain][eventName]['Other']:
                    for line,toplevel in self.ground_test_names.items():
                        if tl == toplevel:
                            path = os.path.sep.join(self.data[domaintype][domain][eventName]['Other'][tl])
                            if path.startswith('**BASE**'):
                                if linuxeventBase and os.path.isdir(linuxeventBase):
                                    line.setText(path.replace('**BASE**',linuxeventBase))
                                elif windowseventBase and os.path.isdir(linuxeventBase):
                                    line.setText(path.replace('**BASE**',windowseventBase))
                            else:
                                line.setText(path)
                for phase in self.data[domaintype][domain][eventName]:
                    if phase in ['Other','Base']:
                        continue
                    for toplevel in self.data[domaintype][domain][eventName][phase]:
                        path = os.path.sep.join(self.data[domaintype][domain][eventName][phase][toplevel])
                        if path.startswith('**BASE**'):
                            if linuxeventBase and os.path.isdir(linuxeventBase):
                                base = path.replace('**BASE**',linuxeventBase)
                            elif windowseventBase and os.path.isdir(windowseventBase):
                                base = path.replace('**BASE**',windowseventBase)
                            else:
                                base = 'ERRORERROR'
                        else:
                            base = path
                        self.add_ground_test_phase(phase,toplevel,base)
            elif domaintype == 'Generic':
                linuxeventBase = self.data[domaintype][domain][eventName]['Path'][0]
                windowseventBase = self.data[domaintype][domain][eventName]['Path'][1]
                self.GenericEventLine.setText(linuxeventBase)
                self.GenericEventLineWindows.setText(windowseventBase)
                # self.GenericExecLine.setText(self.data[domaintype][domain][eventName]['Other']['execution'])
                for phase in self.data[domaintype][domain][eventName]:
                    if phase in ['Other','Path']:
                        continue
                    path = os.path.sep.join(self.data[domaintype][domain][eventName][phase])
                    if path.startswith('**BASE**'):
                        if linuxeventBase and os.path.isdir(linuxeventBase):
                            base = path.replace('**BASE**',linuxeventBase)
                        elif windowseventBase and os.path.isdir(windowseventBase):
                            base = path.replace('**BASE**',windowseventBase)
                        else:
                            base = 'ERROREROR'
                    else:
                        base = path
                    self.add_generic_test_phase(phase,base)
                        
                    
                            
    
### Ground Test Stuff
    
    def update_ground_test_dict(self,line):
        if line.text().startswith(self.EventBaseLine.text()) and self.EventBaseLine.text():
            folderdir = line.text().split(self.EventBaseLine.text())[-1]
        elif line.text().startswith(self.EventBaseWindowsLine.text()) and self.EventBaseWindowsLine.text():
            folderdir = line.text().split(self.EventBaseWindowsLine.text())[-1]
        else:
            folderdir = line.text()
        self.ground_test_dict[line] = folderdir
        self.update_ground_Phase()
        
    def ground_test_autopopulate(self):
        knownadds = ['rfr','tci','eac','dr','tc_dev',self.EventCombo.currentText()]
        phasebases = ['execution','output','data']
        for add in knownadds:
            for base in phasebases:
                self.add_ground_test_phase(add,base)
    
    def fill_ground_paths(self):
        if self.DomainCombo.currentText() and self.EventCombo.currentText():
            event = self.EventCombo.currentText()
            if self.EventBaseLine.text() and event and os.path.isdir(self.EventBaseLine.text()):
                basedir = os.path.join(self.EventBaseLine.text(),event)
                for line in self.ground_test_names:
                    folderdir = self.ground_test_names[line]
                    if self.ground_test_dict[line]=='' or self.ground_test_dict[line].startswith(basedir[:-1]):
                        line.setText(os.path.join(basedir,folderdir))
                        self.ground_test_dict[line] = os.path.join(basedir,folderdir)
            elif self.EventBaseWindowsLine.text() and event and os.path.isdir(self.EventBaseWindowsLine.text()):
                basedir = os.path.join(self.EventBaseWindowsLine.text(),event)
                for line in self.ground_test_names:
                    folderdir = self.ground_test_names[line]
                    if self.ground_test_dict[line]=='' or self.ground_test_dict[line].startswith(basedir[:-1]):
                        line.setText(os.path.join(basedir,folderdir))
                        self.ground_test_dict[line] = os.path.join(basedir,folderdir)
            else:
                for line in self.ground_test_names:
                    line.setText('')
                    self.ground_test_dict[line] = ''
        else:
            print('You need to set a domain and event before this step')
    
    def add_ground_test_phase(self,phase='',ctype='',fulldir=''):
        if ((self.EventBaseLine.text() and os.path.isdir(self.EventBaseLine.text())) or (self.EventBaseWindowsLine.text() and self.EventBaseWindowsLine.text())) and self.EventCombo.currentText():
            item = Widgets.QTreeWidgetItem(self.GroundTestTree)
            item.setFlags(Core.Qt.ItemIsSelectable | Core.Qt.ItemIsEditable | Core.Qt.ItemIsEnabled)
            button = Widgets.QPushButton('Phase Dir')
            combo = Widgets.QComboBox()
            combo.addItems(['','execution','output','data'])
            button.clicked.connect(lambda trash,item=item:self.get_ground_Phase_Dir(item))
            combo.activated.connect(lambda trash:self.update_ground_Phase())
            combo.blockSignals(True)
            index = combo.findText(ctype)
            combo.setCurrentIndex(index)
            combo.blockSignals(False)
            item.setText(2,phase)
            if ctype:
                for line,base in self.ground_test_names.items():
                    if base == ctype:
                        dirline = line
                        break
                    else:
                        dirline = None
            if not fulldir:
                if dirline:
                    fulldir = os.path.join(dirline.text(),phase)
                else:
                    fulldir = ''
                if ctype == 'data':
                    fulldir = ''
            item.setText(3,fulldir)
            self.ComboList.append(combo)
            self.GroundTestTree.setItemWidget(item,0,button)
            self.GroundTestTree.setItemWidget(item,1,combo)
            self.GroundTestTree.addTopLevelItem(item)
            
    def remove_ground_test_phases(self):
        items = self.GroundTestTree.selectedItems()
        rlist = []
        if items:
            for i in range(self.GroundTestTree.topLevelItemCount()):
                item = self.GroundTestTree.topLevelItem(i)
                if item in items:
                    rlist.append(i)
            for index in reversed(rlist):
                self.ComboList.pop(index)
                self.GroundTestTree.takeTopLevelItem(index)
        
    def get_ground_Phase_Dir(self,item):
        if self.DomainCombo.currentText() and self.EventCombo.currentText():
            if self.EventBaseLine.text() and os.path.isdir(self.EventBaseLine.text()):
                curdir = os.path.join(self.EventBaseLine.text())
            elif self.EventBaseWindowsLine.text() and self.EventCombo.currentText():
                curdir = os.path.join(self.EventBaseWindowsLine.text())
            else:
                curdir = os.getcwd()
            dirname = Widgets.QFileDialog.getExistingDirectory(self,'Select a Directory to Point to',curdir,Widgets.QFileDialog.ShowDirsOnly)
            if dirname:
                item.setText(3,dirname)
        else:
            print('You need to set up a domain and event before this step')
    
    def get_ground_Dir(self,line):
        if self.DomainCombo.currentText() and self.EventCombo.currentText():
            if self.EventBaseLine.text() and os.path.isdir(self.EventBaseLine.text()):
                curdir = os.path.join(self.EventBaseLine.text())
            elif self.EventBaseWindowsLine.text() and self.EventCombo.currentText():
                curdir = os.path.join(self.EventBaseWindowsLine.text())
            else:
                curdir = os.getcwd()
            dirname = Widgets.QFileDialog.getExistingDirectory(self,'Select a Directory to Point to',curdir,Widgets.QFileDialog.ShowDirsOnly)
            if dirname:
                line.setText(dirname)
        else:
            print('You need to set up a domain and event before this step')
            
    def update_ground_Phase(self):
        for i in range(self.GroundTestTree.topLevelItemCount()):
            item = self.GroundTestTree.topLevelItem(i)
            combo = self.ComboList[i]
            ctype = combo.currentText()
            for line,base in self.ground_test_names.items():
                if base == ctype:
                    dirline = line
                    break
                else:
                    dirline = None
            if dirline:
                fulldir = os.path.join(line.text(),item.text(2))
                item.setText(3,fulldir)
### Generic Pathing
    def add_generic_test_phase(self,datatype='',fulldir=''):
        if ((self.GenericEventLine.text() and os.path.isdir(self.GenericEventLine.text())) or (self.GenericEventLineWindows.text() and os.path.isdir(self.GenericEventLineWindows.text()))) and self.EventCombo.currentText():
            # and self.GenericExecLine.text() and os.path.isdir(self.GenericExecLine.text()):
            item = Widgets.QTreeWidgetItem(self.GenericTree)
            item.setFlags(Core.Qt.ItemIsSelectable | Core.Qt.ItemIsEditable | Core.Qt.ItemIsEnabled)
            button = Widgets.QPushButton('Data Base Dir')
            button.clicked.connect(lambda trash,item=item:self.get_generic_Data_Dir(item))
            item.setText(1,datatype)
            item.setText(2,fulldir)
            self.GenericTree.setItemWidget(item,0,button)
            self.GenericTree.addTopLevelItem(item)
    
    def remove_generic_test_phases(self):
        items = self.GenericTree.selectedItems()
        rlist = []
        if items:
            for i in range(self.GenericTree.topLevelItemCount()):
                item = self.GroundTestTree.topLevelItem(i)
                if item in items:
                    rlist.append(i)
            for index in reversed(rlist):
                self.GenericTree.takeTopLevelItem(index)
                
    def get_generic_Data_Dir(self,item):
        if self.DomainCombo.currentText() and self.EventCombo.currentText():
            if self.GenericEventLine.text() and os.path.isdir(self.GenericEventLine.text()):
            # if self.GenericExecLine.text() and os.path.isdir(self.GenericExecLine.text()):
                curdir = os.path.join(self.GenericEventLine.text())
            elif self.GenericEventLineWindows.text() and os.path.isdir(self.GenericEventLineWindows.text()):
                curdir = os.path.join(self.GenericEventLineWindows.text())
            else:
                curdir = os.getcwd()
            dirname = Widgets.QFileDialog.getExistingDirectory(self,'Select a Directory to Point to',curdir,Widgets.QFileDialog.ShowDirsOnly)
            if dirname:
                item.setText(2,dirname)
        else:
            print('You need to set up a domain and event before this step')
            
    def get_generic_Dir(self,line):
        if self.DomainCombo.currentText() and self.EventCombo.currentText():
            if self.GenericEventLine.text() and os.path.isdir(self.GenericEventLine.text()):
                curdir = os.path.join(self.GenericEventLine.text())
            elif self.GenericEventLineWindows.text() and os.path.isdir(self.GenericEventLineWindows.text()):
                curdir = os.path.join(self.GenericEventLineWindows.text())
            else:
                curdir = os.getcwd()
            dirname = Widgets.QFileDialog.getExistingDirectory(self,'Select a Directory to Point to',curdir,Widgets.QFileDialog.ShowDirsOnly)
            if dirname:
                line.setText(dirname)
        else:
            print('You need to set up a domain and event before this step')
            
### Saving
    
    def save_json(self):
        domaintype = self.DomainTypeCombo.currentText()
        domain = self.DomainCombo.currentText()
        if domain and domaintype:
            if domaintype == 'Ground Test':
                linuxeventBase = self.EventBaseLine.text()
                windowseventBase = self.EventBaseWindowsLine.text()
                eventName = self.EventCombo.currentText()
                if (linuxeventBase or windowseventBase) and eventName:
                    pdata = {}
                    pdata[eventName] = {'Base':[linuxeventBase,windowseventBase]}
                    pdata[eventName]['Other'] = {}
                    for line in self.ground_test_dict:
                        if line.text().startswith(linuxeventBase) and linuxeventBase:
                            grounddir = line.text().split(linuxeventBase)[-1].split(os.path.sep)
                            if not grounddir[0]:
                                grounddir.pop(0)
                            grounddir.insert(0,'**BASE**')
                        elif line.text().startswith(windowseventBase) and windowseventBase:
                            grounddir = line.text().split(windowseventBase)[-1].split(os.path.sep)
                            if not grounddir[0]:
                                grounddir.pop(0)
                            grounddir.insert(0,'**BASE**')
                        else:
                            grounddir = line.text().split(os.path.sep)
                        pdata[eventName]['Other'][self.ground_test_names[line]] = grounddir
                    for i in range(self.GroundTestTree.topLevelItemCount()):
                        item = self.GroundTestTree.topLevelItem(i)
                        combotext = self.ComboList[i].currentText()
                        phase = item.text(2)
                        if not phase:
                            continue
                        if phase not in pdata[eventName]:
                            pdata[eventName][phase] = {}
                        if item.text(3).startswith(linuxeventBase) and linuxeventBase:
                            phasedir = item.text(3).split(linuxeventBase)[-1].split(os.path.sep)
                            if not phasedir[0]:
                                phasedir.pop(0)
                            phasedir.insert(0,'**BASE**')
                        elif item.text(3).startswith(windowseventBase) and windowseventBase:
                            phasedir = item.text(3).split(windowseventBase)[-1].split(os.path.sep).insert(0,'**BASE**')
                            if not phasedir[0]:
                                phasedir.pop(0)
                            phasedir.insert(0,'**BASE**')
                        else:
                            phasedir = item.text(3).split(os.path.sep)
                        pdata[eventName][phase][combotext] = phasedir
            if domaintype == 'Generic':
                pdata = {}
                eventName = self.EventCombo.currentText()
                linuxeventBase = self.GenericEventLine.text()
                windowseventBase = self.GenericEventLineWindows.text()
                if (linuxeventBase or windowseventBase) and eventName:
                    pdata[eventName] = {'Path':[linuxeventBase,windowseventBase]}
                    for i in range(self.GenericTree.topLevelItemCount()):
                        item = self.GenericTree.topLevelItem(i)
                        phase = item.text(1)
                        if not phase:
                            continue
                        if phase not in pdata[eventName]:
                            pdata[eventName][phase] = {}
                        pdir = item.text(2)
                        if pdir.startswith(linuxeventBase) and linuxeventBase:
                            phasedir = pdir.split(linuxeventBase)[-1].split(os.path.sep)
                            if not phasedir[0]:
                                phasedir.pop(0)
                            phasedir.insert(0,'**BASE**')
                        elif pdir.startswith(windowseventBase) and windowseventBase:
                            phasedir = pdir.split(windowseventBase)[-1].split(os.path.sep)
                            if not phasedir[0]:
                                phasedir.pop(0)
                            phasedir.insert(0,'**BASE**')
                        else:
                            phasedir = pdir.split(os.path.sep)
                        pdata[eventName][phase] = phasedir
            if domaintype not in self.data:
                self.data[domaintype] = {}
            if domain not in self.data[domaintype]:
                self.data[domaintype][domain] = {}
            self.data[domaintype][domain][eventName] = pdata[eventName]
            with open(self.fpath,'w') as jf:
                json.dump(self.data,jf,indent=4)
            
            
if __name__ == '__main__':
    app = Widgets.QApplication(sys.argv)
    frame = Hephaestus()
    frame.show()
    retval = app.exec_()
    sys.exit(retval)
            