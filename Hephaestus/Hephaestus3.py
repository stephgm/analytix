#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 31 13:54:15 2020

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
    
class StringListWidget(Widgets.QDialog):
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
        self.OKname = kwargs.get('OKname','Confirm')
        if not isinstance(self.OKname,string_types):
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
        # self.SearchBar = SearchBar(self.ListWidget,self,regex=False)
        self.OKButton = Widgets.QPushButton(self.OKname)
        self.OKButton.clicked.connect(lambda:self.addSelected())
        # self.layout.addWidget(self.SearchBar)
        self.layout.addWidget(self.ListWidget)
        self.AddItemButton = Widgets.QPushButton('Add Item')
        self.AddItemButton.clicked.connect(lambda:self.addItemToList())
        self.layout.addWidget(self.AddItemButton)
        if self.addSelectAll:
            self.SelectAllButton = Widgets.QPushButton('Select All')
            self.SelectAllButton.clicked.connect(self.ListWidget.selectAll)
            self.layout.addWidget(self.SelectAllButton)
        self.layout.addWidget(self.OKButton)
        
    def addItemToList(self):
        item = popUpSimpleText('Add Item')
        if item:
            self.ListWidget.addItem(item)

    def setList(self,items):
        if not isinstance(items,list):
            print('items passed to setList in {}, was not a list.  Returning'.format(self.n))
            return
        if not isinstance(items[0],string_types):
            print('items passed to setList in {}, were not string types.  Returning'.format(self.n))
            return
        self.ListWidget.clear()
        self.listItems = copy.copy(items)
        self.ListWidget.addItems(self.listItems)
        self.updated.emit()

    def addSelected(self):
        selectedHeaders = returnListSelection(self.ListWidget)
        self.getSelection.emit(selectedHeaders)
        return selectedHeaders
        
    def removeItems(self,items):
        self.ListWidget.clear()
        if not isinstance(items,list):
            items = [items]
        for item in items:
            if item in self.listItems:
                self.listItems.pop(self.listItems.index(item))
        self.setList(self.listItems)
        
def popUpListWidget(items,**kwargs):
    lw = StringListWidget(items,**kwargs)
    lw.getSelection.connect(lambda:lw.close())
    lw.exec_()
    return lw.addSelected()

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
        if not isinstance(MessageText,string_types):
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

os.environ['TOOLS_CONFIG_DIR'] = os.path.join(os.path.expanduser('~'),'Desktop')


if os.name == 'posix':
    INDEX = 0
else:
    INDEX = 1

class Hephaestus(Widgets.QMainWindow):
    def __init__(self, parent=None):
        Widgets.QMainWindow.__init__(self, parent)
        Qt5.loadUi('Hephaestus3.ui', self)
        
        self.enable_os_specific(enableall=self.EnableAllPathsCheck.isChecked())
        self.read_json_file()
        self.makeConnections()
        
    def correct_windows_paths(self,path):
        return path.replace('/','\\')
    
    def correct_linux_paths(self,path):
        return path.replace('\\','/')
        
    def read_json_file(self):
        self.re_init()
        
        self.fpath = os.path.join(os.environ['TOOLS_CONFIG_DIR'],'EventConfig.json')
        if os.path.isfile(self.fpath):
            with open(self.fpath,'r') as jf:
                self.data = json.load(jf)
        else:
            with open(self.fpath,'w') as jf:
                json.dump({},jf)
            self.data = {}
        
        self.populate_domains()
        self.populate_events()
        self.check_domain_event()
        
    def enable_os_specific(self,**kwargs):
        if self.DomainCombo.currentText() and self.EventCombo.currentText():
            enableall = kwargs.get('enableall',False)
            qlines = self.findChildren(Widgets.QLineEdit)
            qbuttons = self.findChildren(Widgets.QPushButton)
            for line in qlines:
                if 'windows' in line.objectName().lower() and not enableall and INDEX==0:
                    line.setEnabled(False)
                elif 'linux' in line.objectName().lower() and not enableall and INDEX == 1:
                    line.setEnabled(False)
                else:
                    line.setEnabled(True)
            for button in qbuttons:
                if 'windows' in button.objectName().lower() and not enableall and INDEX==0:
                    button.setEnabled(False)
                elif 'linux' in button.objectName().lower() and not enableall and INDEX == 1:
                    button.setEnabled(False)
                else:
                    if 'AutoCompleteDigestPath' in button.objectName():
                        button.setEnabled(True)
                    if 'AutoSetup' in button.objectName():
                        button.setEnabled(True)
                    
    
    def re_init(self):
        # Ground Test Convenience Structures
        self.ground_test_dir_dict = {'Linux':{self.EventPathLinuxLine:[self.EventPathLinuxButton,''],
                                              self.ConfigPathLinuxLine:[self.ConfigPathLinuxButton,'config'],
                                              self.ExecPathLinuxLine:[self.ExecPathLinuxButton,'execution'],
                                              self.OutputPathLinuxLine:[self.OutputPathLinuxButton,'output'],
                                              self.DoxPathLinuxLine:[self.DoxPathLinuxButton,'documentation'],
                                              self.DataPathLinuxLine:[self.DataPathLinuxButton,'data'],
                                              self.OSFPathLinuxLine:[self.OSFPathLinuxButton,'osf'],
                                              self.ITPPathLinuxLine:[self.ITPPathLinuxButton,'itp']},
                                     
                                     'Windows':{self.EventPathWindowsLine:[self.EventPathWindowsButton,''],
                                              self.ConfigPathWindowsLine:[self.ConfigPathWindowsButton,'config'],
                                              self.ExecPathWindowsLine:[self.ExecPathWindowsButton,'execution'],
                                              self.OutputPathWindowsLine:[self.OutputPathWindowsButton,'output'],
                                              self.DoxPathWindowsLine:[self.DoxPathWindowsButton,'documentation'],
                                              self.DataPathWindowsLine:[self.DataPathWindowsButton,'data'],
                                              self.OSFPathWindowsLine:[self.OSFPathWindowsButton,'osf'],
                                              self.ITPPathWindowsLine:[self.ITPPathWindowsButton,'itp']}}
        # MAT Convenience Structures
        self.MAT_dir_dict = {'Linux':{},
                             'Windows':{}}
        
        
        qlines = self.findChildren(Widgets.QLineEdit)
        for line in qlines:
            line.clear()
        qtrees = self.findChildren(Widgets.QTreeWidget)
        for tree in qtrees:
            tree.clear()
            
        self.ComboList = []
        self.OSComboList = []
        self.ButtonList = []
        
    def makeConnections(self):
        
        #General Signals
        self.DomainTypeCombo.currentIndexChanged.connect(lambda trash:self.populate_domains())
        self.DomainCombo.currentIndexChanged.connect(lambda trash:self.populate_events())
        self.EventCombo.currentIndexChanged.connect(lambda trash:self.populate_paths())
        
        self.DomainTypeCombo.currentIndexChanged.connect(lambda trash:self.check_domain_event())
        self.DomainCombo.currentIndexChanged.connect(lambda trash:self.check_domain_event())
        self.EventCombo.currentIndexChanged.connect(lambda trash:self.check_domain_event())
        
        self.AddDomainButton.clicked.connect(lambda trash:self.add_new_domain())
        self.AddEventButton.clicked.connect(lambda trash:self.add_new_event())
        
        self.EnableAllPathsCheck.toggled.connect(lambda toggle:self.enable_os_specific(enableall=toggle))
        
        self.SaveButton.clicked.connect(lambda trash:self.save_json())
        
        #Ground Test Signals
        self.AutoCompleteDigestPathsLinux.clicked.connect(lambda trash:self.autopopulate_digest_paths('linux'))
        self.AutoCompleteDigestPathsWindows.clicked.connect(lambda trash:self.autopopulate_digest_paths('windows'))
        
        for OS in self.ground_test_dir_dict:
            for line,value in self.ground_test_dir_dict[OS].items():
                line.textChanged.connect(lambda trash:self.update_phase_dir())
                print(value)
                value[0].clicked.connect(lambda trash,line=line:self.get_dir(line))
        self.GTAddPhaseButton.clicked.connect(lambda trash:self.add_ground_test_phase())
        self.GTRemovePhasesButton.clicked.connect(lambda trash:self.remove_ground_test_phases())
        self.GTPhasesAutoSetupLinux.clicked.connect(lambda trash:self.autopopulate_ground_test_phases('linux'))
        self.GTPhasesAutoSetupWindows.clicked.connect(lambda trash:self.autopopulate_ground_test_phases('windows'))
                
        pass
    
    def get_dir(self,obj):
        #TODO, make sure paths are separated correctly, however opposite OS buttons should not be able to come here
        domain = self.DomainCombo.currentText()
        event = self.EventCombo.currentText()
        if event and domain:
            if isinstance(obj,Widgets.QLineEdit):
                if 'windows' in obj.objectName().lower() and self.EventPathWindowsLine.text() and os.path.isdir(self.EventPathWindowsLine.text()):
                    curdir = self.correct_windows_paths(self.EventPathWindowsLine.text())
                elif 'linux' in obj.objectName().lower() and self.EventPathLinuxLine.text() and os.path.isdir(self.EventPathLinuxLine.text()):
                    curdir = self.correct_linux_paths(self.EventPathLinuxLine.text())
                else:
                    curdir = os.getcwd()
                dirname = Widgets.QFileDialog.getExistingDirectory(self,'Select a Directory to Point to',curdir,Widgets.QFileDialog.ShowDirsOnly)
                if dirname:
                    if not 'EventPath' in obj.objectName():
                        obj.setText(dirname)
                    else:
                        if os.path.basename(dirname) != event:
                            obj.setText(os.path.join(dirname,event))
                        else:
                            obj.setText(dirname)
            elif isinstance(obj,Widgets.QTreeWidgetItem):
                if obj.treeWidget() == self.GTPhaseTree:
                    for i in range(self.GTPhaseTree.topLevelItemCount()):
                        item = self.GTPhaseTree.topLevelItem(i)
                        ostype = self.OSComboList[i].currentText()
                        if obj == item:
                            if 'windows' in ostype.lower() and self.EventPathWindowsLine.text() and os.path.isdir(self.EventPathWindowsLine.text()):
                                curdir = self.correct_windows_paths(self.EventPathWindowsLine.text())
                            elif 'linux' in ostype.lower() and self.EventPathLinuxLine.text() and os.path.isdir(self.EventPathLinuxLine.text()):
                                curdir = self.correct_linux_paths(self.EventPathLinuxLine.text())
                            else:
                                curdir = os.getcwd()
                            dirname = Widgets.QFileDialog.getExistingDirectory(self,'Select a Directory to Point to',curdir,Widgets.QFileDialog.ShowDirsOnly)
                            if dirname:    
                                obj.setText(4,dirname)
            else:
                return
        else:
            print('You need to set up a domain and event before this step')
            
    def check_domain_event(self):
        if self.DomainCombo.currentText() and self.EventCombo.currentText():
            enable = True
        else:
            enable = False
        qlines = self.findChildren(Widgets.QLineEdit)
        qtrees = self.findChildren(Widgets.QTreeWidget)
        qbuttons = [f for f in self.findChildren(Widgets.QPushButton) if 'windows' in f.objectName().lower() or 'linux' in f.objectName().lower()]
        for line in qlines:
            line.setEnabled(enable)
        for tree in qtrees:
            tree.setEnabled(enable)
        for button in qbuttons:
            button.setEnabled(enable)
        self.enable_os_specific(enableall=self.EnableAllPathsCheck.isChecked())
        
    def remove_event(self):
        domaintype = self.DomainTypeCombo.currentText()
        domain = self.DomainCombo.currentText()
        event = self.EventCombo.currentText()
        if domain and event:
            confirmed = MessageBox(f'Are you sure you want to delete {event} from the {domain} domain?')
            if confirmed:
                if domaintype in self.data and domain in self.data[domaintype] and event in self.data[domaintype][domain]:
                    self.data[domaintype][domain].pop(event)
    
    def remove_domain(self):
        domaintype = self.DomainTypeCombo.currentText()
        domain = self.DomainCombo.currentText()
        if domain:
            confirmed = MessageBox(f'Are you sure you want to delete the domain {domain}?  This will remove all events inside the domain.')
            if confirmed:
                if domaintype in self.data and domain in self.data[domaintype]:
                    self.data[domaintype].pop(domain)
            
    def add_new_domain(self):
        domain = popUpSimpleText('Domain Name:', title='Enter Domain')
        if domain:
            self.DomainCombo.addItem(domain)
            index = self.DomainCombo.findText(domain)
            self.DomainCombo.setCurrentIndex(index)
            
    def add_new_event(self):
        if self.DomainCombo.currentText():
            AllEvents = [self.EventCombo.itemText(i) for i in range(self.EventCombo.count())]
            if self.DomainTypeCombo.currentText() == 'Ground Test':
                exists = YesNoMessageBox('Does the event you are about to add already established?')
                if exists:
                    standard = YesNoMessageBox('Does the event follow the standard setup method?')
                    eventdirectory = os.path.realpath(Widgets.QFileDialog.getExistingDirectory(self,'Point to the Event Folder',os.getcwd(),Widgets.QFileDialog.ShowDirsOnly))
                    if eventdirectory:
                        event = os.path.basename(eventdirectory)
                        if event not in AllEvents:
                            self.EventCombo.addItem(event)
                            index = self.EventCombo.findText(event)
                            self.EventCombo.setCurrentIndex(index)
                            if INDEX == 0:
                                self.EventPathLinuxLine.setText(self.correct_linux_paths(eventdirectory))
                            else:
                                self.EventPathWindowsLine.setText(self.correct_windows_paths(eventdirectory))
                            if standard:
                                if INDEX == 0:
                                    self.autopopulate_digest_paths('linux')
                                    OS = 'linux'
                                else:
                                    self.autopopulate_digest_paths('windows')
                                    OS = 'windows'
                                #TODO, just scan the execution directory to get the phases
                                directories = []
                                if OS == 'linux':
                                    if self.ExecPathLinuxLine.text() and os.path.isdir(self.ExecPathLinuxLine.text()):
                                        directories = [p for p in os.listdir(self.ExecPathLinuxLine.text()) if os.path.isdir(p)]
                                elif OS == 'windows':
                                    if self.ExecPathWindowsLine.text() and os.path.isdir(self.ExecPathWindowsLine.text()):
                                        directories = [p for p in os.listdir(self.ExecPathWindowsLine.text()) if os.path.isdir(p)]
                                self.autopopulate_ground_test_phases(OS, phases=directories)
                                return
                            else:
                                return
                                
                        else:
                            MessageBox('The event you have pointed to already exists', title='Event Already Exists')
                            index = self.EventCombo.findText(event)
                            self.EventCombo.setCurrentIndex(index)
                            return
                    else:
                        return
                else:
                    event = popUpSimpleText('Event Name:', title = 'Enter Event')
                    if event:
                        if event not in AllEvents:
                            standard = YesNoMessageBox('Do you want the event to follow standard setup?')
                            self.EventCombo.addItem(event)
                            index = self.EventCombo.findText(event)
                            self.EventCombo.setCurrentIndex(index)
                            eventbasedirectory = os.path.realpath(Widgets.QFileDialog.getExistingDirectory(self,'Point to where you want the Event Folder to be Placed',os.getcwd(),Widgets.QFileDialog.ShowDirsOnly))
                            if eventbasedirectory:
                                if INDEX == 0:
                                    self.EventPathLinuxLine.setText(os.path.join(eventbasedirectory,event))
                                else:
                                    self.EventPathWindowsLine.setText(self.correct_windows_paths(os.path.join(eventbasedirectory,event)))
                                if standard:
                                    if INDEX == 0:
                                        self.autopopulate_digest_paths('linux')
                                        OS = 'linux'
                                    else:
                                        self.autopopulate_digest_paths('windows')
                                        OS = 'windows'
                                    self.autopopulate_ground_test_phases(OS)
                                    makedirs = YesNoMessageBox('Create the directories?')
                                    if makedirs:
                                        self.make_ground_test_dirs()
                                        self.save_json()
                                        
                        else:
                            MessageBox('The event you have pointed to already exists', title='Event Already Exists')
                            index = self.EventCombo.findText(event)
                            self.EventCombo.setCurrentIndex(index)
                            return
            else:
                event = popUpSimpleText('Event Name:', title='Enter Event')
                if event:
                    if event not in AllEvents:
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
        self.re_init()
        domaintype = self.DomainTypeCombo.currentText()
        domain = self.DomainCombo.currentText()
        event = self.EventCombo.currentText()
        if domain and event:
            if domaintype in self.data and domain in self.data[domaintype] and event in self.data[domaintype][domain]:
                basedict = self.data[domaintype][domain][event]        
                if domaintype == 'Ground Test':
                    #Event Paths
                    self.EventPathLinuxLine.setText(basedict['EventPath'][0])
                    self.EventPathWindowsLine.setText(basedict['EventPath'][1])
                    #Digest Paths
                    for dptype in basedict['DigestDirs']:
                        for OS in ['Linux','Windows']:
                            if OS == 'Linux':
                                idx = 0
                            else:
                                idx = 1
                            for line,vals in self.ground_test_dir_dict[OS].items():
                                if vals[1]:
                                    if vals[1] == dptype:
                                        line.setText(basedict['DigestDirs'][dptype][idx])
                    #Phase Paths
                    for phase in basedict['PhaseDirs']:
                        for ctype in basedict['PhaseDirs'][phase]:
                            for i,directory in enumerate(basedict['PhaseDirs'][phase][ctype]):
                                if directory or ctype == 'data':
                                    if i == 0:
                                        ostype = 'Linux'
                                    else:
                                        ostype = 'Windows'
                                    self.add_ground_test_phase(phase,ctype,ostype,directory)
                else:
                    #TODO, add for MAT and Generic
                    return
            else:
                #TODO, Add warning popup
                return
### Ground Test Stuff
    def autopopulate_digest_paths(self,OS):
        event = self.EventCombo.currentText()
        domain = self.DomainCombo.currentText()
        if domain and event:
            if 'linux' in OS.lower():
                key = 'Linux'
                base = self.EventPathLinuxLine.text()
            else:
                key = 'Windows'
                base = self.EventPathWindowsLine.text()
            
            for line,vals in self.ground_test_dir_dict[key].items():
                if vals[1]:
                    directory = os.path.join(base,self.ground_test_dir_dict[key][line][1])
                    if key == 'Windows':
                        directory = self.correct_windows_paths(directory)
                    else:
                        directory = self.correct_linux_paths(directory)
                    line.setText(directory)
            
    def autopopulate_ground_test_phases(self,OS,**kwargs):
        showWarning = kwargs.pop('showWarning',True)
        phases = kwargs.pop('phases',[])
        event = self.EventCombo.currentText()
        domain = self.DomainCombo.currentText()
        if 'windows' in OS.lower():
            OS = 'Windows'
            basedir = self.EventPathWindowsLine.text()
        else:
            OS = 'Linux'
            basedir = self.EventPathLinuxLine.text()
        if event and domain and basedir:
            if not phases:
                phases = popUpListWidget(['rfr','tci','esa','eci','tc_dev',event],selection=2,title='Select Phases')
            if phases:
                for phase in phases:
                    for base in ['output','execution','data']:
                        for line,vals in self.ground_test_dir_dict[OS].items():
                            if vals[1] and vals[1] == base and base != 'data':
                                fulldir = os.path.join(line.text(),phase)
                                if OS == 'Windows':
                                    fulldir = self.correct_windows_paths(fulldir)
                                else:
                                    fulldir = self.correct_linux_paths(fulldir)
                                break
                            else:
                                fulldir = ''
                        self.add_ground_test_phase(phase,base,OS,fulldir)
                if showWarning:
                    MessageBox('Please set up the data Phases to point to their correct locations.')
        
    def add_ground_test_phase(self,phase='',ctype='',ostype='',fulldir=''):
        domain = self.DomainCombo.currentText()
        event = self.EventCombo.currentText()
        if domain and event and (self.EventPathLinuxLine.text() or self.EventPathWindowsLine.text()):
            item = Widgets.QTreeWidgetItem(self.GTPhaseTree)
            item.setFlags(Core.Qt.ItemIsSelectable | Core.Qt.ItemIsEditable | Core.Qt.ItemIsEnabled)
            button = Widgets.QPushButton('Phase Dir')
            oscombo = Widgets.QComboBox()
            oscombo.addItems(['Linux','Windows'])
            combo = Widgets.QComboBox()
            combo.addItems(['','execution','output','data'])
            button.clicked.connect(lambda trash,item=item:self.get_dir(item))
            combo.blockSignals(True)
            index = combo.findText(ctype)
            combo.setCurrentIndex(index)
            combo.blockSignals(False)
            oscombo.blockSignals(True)
            index = oscombo.findText(ostype)
            oscombo.setCurrentIndex(index)
            oscombo.blockSignals(False)
            item.setText(3,phase)
            if ctype and not fulldir:
                for line,base in self.ground_test_dir_dict.items():
                    if base == ctype:
                        dirline = line
                        break
                    else:
                        dirline = None
            else:
                dirline = None
            if not fulldir:
                if dirline:
                    fulldir = os.path.join(dirline.text(),phase)
                else:
                    fulldir = ''
                if ctype == 'data':
                    fulldir = ''
            item.setText(4,fulldir)
            
            combo.currentIndexChanged.connect(lambda trash,item=item:self.check_phase_button(item))
            combo.currentIndexChanged.connect(lambda trash:self.update_phase_dir())
            oscombo.currentIndexChanged.connect(lambda trash:self.check_phase_button(item))
            oscombo.currentIndexChanged.connect(lambda trash:self.update_phase_dir())
            
            self.ComboList.append(combo)
            self.OSComboList.append(oscombo)
            self.ButtonList.append(button)
            self.GTPhaseTree.setItemWidget(item,0,oscombo)
            self.GTPhaseTree.setItemWidget(item,1,combo)
            self.GTPhaseTree.setItemWidget(item,2,button)
            self.GTPhaseTree.addTopLevelItem(item)
            
            self.check_phase_button(item)
            
    def remove_ground_test_phases(self):
        items = self.GTPhaseTree.selectedItems()
        rlist = []
        if items:
            for i in range(self.GTPhaseTree.topLevelItemCount()):
                item = self.GTPhaseTree.topLevelItem(i)
                if item in items:
                    rlist.append(i)
            for index in reversed(rlist):
                self.ComboList.pop(index)
                self.OSComboList.pop(index)
                self.GTPhaseTree.takeTopLevelItem(index)
    
    def check_phase_button(self,item):
        #Block buttons that are based off a ground test dir
        #Furthermore block out opposite OS buttons no matter what
        if INDEX == 0:
            OS = 'Linux'
        else:
            OS = 'Windows'
        for i in range(self.GTPhaseTree.topLevelItemCount()):
            treeitem = self.GTPhaseTree.topLevelItem(i)
            if item != treeitem:
                continue
            combotext = self.ComboList[i].currentText()
            ostype = self.OSComboList[i].currentText()
            if (combotext and combotext != 'data') or OS != ostype:
                self.ButtonList[i].setEnabled(False)
            else:
                self.ButtonList[i].setEnabled(True)
    
    def update_phase_dir(self):
        #Was set up for passing the item.. but nah Cant do because of ground test dirs dont have access to the item
        for i in range(self.GTPhaseTree.topLevelItemCount()):
            treeitem = self.GTPhaseTree.topLevelItem(i)
            combotext = self.ComboList[i].currentText()
            ostext = self.OSComboList[i].currentText()
            if combotext:
                for line,vals in self.ground_test_dir_dict[ostext].items():
                    if vals[1] == combotext and combotext != 'data':
                        base = line.text()
                        break
                    else:
                        base = ''
                if base:
                    if ostext == 'Windows':
                        fulldir = self.correct_windows_paths(os.path.join(base,treeitem.text(3)))
                    else:
                        fulldir = self.correct_linux_paths(os.path.join(base,treeitem.text(3)))
                    treeitem.setText(4,fulldir)
                elif combotext == 'data':
                    continue
                else:
                    treeitem.setText(4,'')
            else:
                treeitem.setText(4,'')
                
    def make_ground_test_dirs(self):
        #Only make dirs if they dont exist... and only for the os that you are ON
        domain = self.DomainCombo.currentText()
        event = self.EventCombo.currentText()
        if event and domain:
            if INDEX == 0:
                OS = 'Linux'
                eventpath = self.EventPathLinuxLine.text()
            else:
                OS = 'Windows'
                eventpath = self.EventPathWindowsLine.text()
            if not os.path.isdir(eventpath):
                os.makedirs(eventpath)
            for line,vals in self.ground_test_dir_dict[OS].items():
                if vals[1]:
                    if OS == 'Linux':
                        idx = 0
                    else:
                        idx = 1
                    if not os.path.isdir(line.text()):
                        os.makedirs(line.text())
                    if vals[1] == 'data':
                        #TODO, make the data directories according to Joel
                        pass
            for i in range(self.GTPhaseTree.topLevelItemCount()):
                item = self.GTPhaseTree.topLevelItem(i)
                ostype = self.OSComboList[i].currentText()
                combotext = self.ComboList[i].currentText()
                phase = item.text(3)
                directory = item.text(4)
                if ostype != OS:
                    continue
                if OS == 'Linux':
                    idx = 0
                else:
                    idx = 1
                if phase and directory:
                    if not os.path.isdir(directory):
                        os.makedirs(directory)
### Saving
    def save_json(self):
        domaintype = self.DomainTypeCombo.currentText()
        domain = self.DomainCombo.currentText()
        pdata = {}
        if domain and domaintype:
            if domaintype == 'Ground Test':
                linuxevent = self.EventPathLinuxLine.text()
                windowsevent = self.EventPathWindowsLine.text()
                eventName = self.EventCombo.currentText()
                pdata[eventName] = {'EventPath':[linuxevent,windowsevent]}
                pdata[eventName]['PhaseDirs'] ={}
                pdata[eventName]['DigestDirs'] ={}
                pdata[eventName]['Other'] = {}
                for OS in ['Linux','Windows']:
                    for line,vals in self.ground_test_dir_dict[OS].items():
                        if vals[1]:
                            if vals[1] not in pdata[eventName]['DigestDirs']:
                                pdata[eventName]['DigestDirs'][vals[1]] = ['','']
                            if OS == 'Linux':
                                idx = 0
                            else:
                                idx = 1
                            pdata[eventName]['DigestDirs'][vals[1]][idx] = line.text()
                    for i in range(self.GTPhaseTree.topLevelItemCount()):
                        item = self.GTPhaseTree.topLevelItem(i)
                        ostype = self.OSComboList[i].currentText()
                        combotext = self.ComboList[i].currentText()
                        phase = item.text(3)
                        directory = item.text(4)
                        if phase:
                            if phase not in pdata[eventName]['PhaseDirs']:
                                pdata[eventName]['PhaseDirs'][phase] = {}
                            if combotext:
                                if combotext not in pdata[eventName]['PhaseDirs'][phase]:
                                    pdata[eventName]['PhaseDirs'][phase][combotext] = ['','']
                            else:
                                #TODO, How to handle extras.. Do We NEED?
                                if 'Extra' not in pdata[eventName]['PhaseDirs'][phase]:
                                    pdata[eventName]['PhaseDirs'][phase][combotext] = ['','']
                            if ostype == 'Linux':
                                idx = 0
                            else:
                                idx = 1
                            pdata[eventName]['PhaseDirs'][phase][combotext][idx] = directory
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
            