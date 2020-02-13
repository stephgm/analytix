#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 12 18:49:53 2020

@author: Carl
"""

import os
import sys
import json

import PyQt5.QtWidgets as Widgets
import PyQt5.QtGui as Gui
import PyQt5.QtCore as Core
from PyQt5 import uic
from six import string_types
import glob
import re

debug = True

if os.name == 'posix':
    rootpathname = '/'
else:
    rootpathname = os.path.splitdrive(sys.executable)[0]

if os.path.isfile(os.path.realpath(__file__)):
    RELATIVE_LIB_PATH = os.path.realpath(__file__)
    while os.path.basename(RELATIVE_LIB_PATH) != 'src' and RELATIVE_LIB_PATH != rootpathname:
        RELATIVE_LIB_PATH = os.path.dirname(RELATIVE_LIB_PATH)
    if __name__ == '__main__':
        sys.path.append(RELATIVE_LIB_PATH)
        sys.path.pop(0)
else:
    RELATIVE_LIB_PATH = os.path.dirname(sys.executable)

import utils.PhobosFunctions as PF
import hmi_utils.QtUtils as QU

class AresConfig():
    def __init__(self,**kwargs):
        self.EventConfig = {}
        self.Paths_to_Runs = {}
        self.Paths_in_Execution = {}
        self.Paths_in_Output = {}
        self.Paths_in_Data = {}
        
        self.itpPaths = {}
        self.EventConfigPath = ''
        
        self.readEventConfig()
        
        if os.name == 'posix':
            self.OS = 'Linux'
            self.idx = 0
        else:
            self.OS = 'Windows'
            self.idx = 1
        
    def readEventConfig(self):
        self.EventConfigPath = os.path.join(os.environ['TOOL_DOMAIN_CONFIG'])
        if os.path.isfile(self.EventConfigPath):
            with open(self.EventConfigPath,'r') as jf:
                self.EventConfig = json.load(jf)
    
    def build_paths_for_runs(self,**kwargs):
        
        get_domaintypes = kwargs.get('get_domaintypes',[])
        get_phases = kwargs.get('get_phases',[])
        
        if self.EventConfig:
            for domaintype in self.EventConfig:
                if get_domaintypes:
                    if domaintype not in get_domaintypes:
                        continue
                self.Paths_to_Runs[domaintype] = {}
                for domain in self.EventConfig[domaintype]:
                    if domain not in self.Paths_to_Runs[domaintype]:
                        self.Paths_to_Runs[domaintype][domain] = {}
                    for event in self.EventConfig[domaintype][domain]:
                        if event not in self.Paths_to_Runs[domaintype][domain]:
                            self.Paths_to_Runs[domaintype][domain][event] = {}
                        if domaintype in ['Ground Test']:
                            for phase,top_level in self.EventConfig[domaintype][domain][event]['PhaseDirs'].items():
                                if 'execution' in top_level:
                                    if get_phases:
                                        if phase not in get_phases:
                                            continue
                                    self.Paths_to_Runs[domaintype][domain][event][phase] = top_level['execution'][self.idx]
                            if 'Referent' in self.EventConfig[domaintype][domain][event]['Other']:
                                self.Paths_to_Runs[domaintype][domain][event]['Referent'] = self.EventConfig[domaintype][domain][event]['Other']['Referent'][self.idx]
                        elif domaintype in ['MAT']:
                            self.Paths_to_Runs[domaintype][domain][event]['ekvsim'] = self.EventConfig[domaintype][domain][event]['EKV Dirs']['ekvsim'][self.idx]
                            self.Paths_to_Runs[domaintype][domain][event]['ekvref'] = self.EventConfig[domaintype][domain][event]['EKV Dirs']['ekvref'][self.idx]
                        elif domaintype in ['Generic']:
                            for key in self.EventConfig[domaintype][domain][event]:
                                self.Paths_to_Runs[domaintype][domain][event][key] = self.EventConfig[domaintype][domain][event][key][self.idx]
        return self.Paths_to_Runs
    
    def build_paths_for_output(self,**kwargs):
        
        get_domaintypes = kwargs.get('get_domaintypes',[])
        get_phases = kwargs.get('get_phases',[])
        
        if self.EventConfig:
            for domaintype in self.EventConfig:
                if get_domaintypes:
                    if domaintype not in get_domaintypes:
                        continue
                self.Paths_in_Output[domaintype] = {}
                for domain in self.EventConfig[domaintype]:
                    if domain not in self.Paths_in_Output[domaintype]:
                        self.Paths_in_Output[domaintype][domain] = {}
                    for event in self.EventConfig[domaintype][domain]:
                        if event not in self.Paths_in_Output[domaintype][domain]:
                            self.Paths_in_Output[domaintype][domain][event] = {}
                        if domaintype in ['Ground Test']:
                            for phase,top_level in self.EventConfig[domaintype][domain][event]['PhaseDirs'].items():
                                if 'output' in top_level:
                                    if get_phases:
                                        if phase not in get_phases:
                                            continue
                                    self.Paths_in_Output[domaintype][domain][event][phase] = top_level['output'][self.idx]
                            if 'Referent' in self.EventConfig[domaintype][domain][event]['Other']:
                                self.Paths_in_Output[domaintype][domain][event]['Referent'] = self.EventConfig[domaintype][domain][event]['Other']['Referent'][self.idx]
                        elif domaintype in ['MAT']:
                            self.Paths_in_Output[domaintype][domain][event]['ekvsim'] = self.EventConfig[domaintype][domain][event]['EKV Dirs']['ekvsim'][self.idx]
                            self.Paths_in_Output[domaintype][domain][event]['ekvref'] = self.EventConfig[domaintype][domain][event]['EKV Dirs']['ekvref'][self.idx]
                        elif domaintype in ['Generic']:
                            for key in self.EventConfig[domaintype][domain][event]:
                                self.Paths_in_Output[domaintype][domain][event][key] = self.EventConfig[domaintype][domain][event][key][self.idx]
        return self.Paths_in_Output
                
    def build_paths_for_itp(self,**kwargs):
        get_domaintypes = kwargs.get('get_domaintypes',[])
        get_phases = kwargs.get('get_phases',[])
        if self.EventConfig:
            for domaintype in self.EventConfig:
                if get_domaintypes:
                    if domaintype not in get_domaintypes:
                        continue
                self.itpPaths[domaintype] = {}
                for domain in self.EventConfig[domaintype]:
                    if domain not in self.itpPaths[domaintype]:
                        self.itpPaths[domaintype][domain] = {}
                    for event in self.EventConfig[domaintype][domain]:
                        if domaintype in ['Ground Test']:
                            self.itpPaths[domaintype][domain][event] = self.EventConfig[domaintype][domain][event]['DigestDirs']['itp'][self.idx]
                        else:
                            self.itpPaths[domaintype][domain][event] = ''
        return self.itpPaths
    

class PathWidget(Widgets.QWidget):
    RunPathChanged = Core.pyqtSignal(object)
    RunPathsChanged = Core.pyqtSignal(object)
    ExecutionPathChanged = Core.pyqtSignal(object)
    OutputPathChanged = Core.pyqtSignal(object)
    ItpPathChanged = Core.pyqtSignal(object)
    
    def __init__(self,parent=None,domaintypes=[],phases=[],**kwargs):
        '''
        This is the init for the GUI controlled combos
        
        Input:
            parent - The parent widget
            domaintypes - The domaintypes that you want to be visible.  Empty List means get all
            phases - The phases that you want to be visible.  Empty List means get all
        Kwargs:
            Holy heck... where to begin.  This is why I like making stuff like this.
        '''
        super(PathWidget,self).__init__(parent)
        
        self.parent = parent
        if isinstance(domaintypes,string_types):
            if domaintypes:
                domaintypes = [domaintypes]
            else:
                domaintypes = []
        self.domaintypes = domaintypes
        if isinstance(phases,string_types):
            if phases:
                phases = [phases]
            else:
                phases = []
        self.phases = phases
        
        self.xx = AresConfig()
        self.PathData = self.xx.build_paths_for_runs(get_domaintypes=self.domaintypes,get_phases=self.phases)
        self.OutputPaths = self.xx.build_paths_for_output(get_domaintypes=self.domaintypes,get_phases=self.phases)
        self.ItpPaths = self.xx.build_paths_for_itp(get_domaintypes=self.domaintypes,get_phases=self.phases)
        
        
        #Kwargs section
        self.showDomainType = kwargs.get('showDomainType',True)
        self.showRun = kwargs.get('showRun',True)
        self.showPhase = kwargs.get('showPhase',True)
        self.multiRun = kwargs.get('multiRun',False)
        self.orientation = kwargs.get('orientation','vertical')
        self.runType = kwargs.get('runType','combo')
        
        if self.orientation not in ['vertical','horizontal','stacked']:
            self.orientation = 'vertical'
        if self.runtype not in ['combo','list']:
            self.runtype = 'combo'
            
        self.layout = Widgets.QGridLayout()
        self.setLayout(self.layout)
        
        self.makeWidget()
        # self.makeConnections()
        
        # self.populate_domain_types()
        
    def makeWidget(self):
        self.DomainTypeLabel = Widgets.QLabel('Domain Type')
        self.DomainLabel = Widgets.QLabel('Domain')
        self.EventLabel = Widgets.QLabel('Event')
        self.PhaseLabel = Widgets.QLabel('Phase')
        self.RunLabel = Widgets.QLabel('Run')
        self.RunsLabel = Widgets.QLabel('Runs')
        
        self.DomainTypeCombo = Widgets.QComboBox()
        self.DomainCombo = Widgets.QComboBox()
        self.EventCombo = Widgets.QComboBox()
        self.RunCombo = Widgets.QComboBox()
        self.PhaseCombo = Widgets.QComboBox()
        
        self.RunsList = Widgets.QListWidget()
        
        if self.multiRun:
            self.RunsList.setSelectionMode(Widgets.QAbstractItemView.ExtendedSelection)
        else:
            self.RunsList.setSelectionMode(Widgets.QAbstractItemView.SingleSelection)
            
        self.SelectAll = Widgets.QPushButton('Select All')
        self.SelectAll.clicked.connect(self.RunsList.selectAll)
        self.DeSelectAll = Widgets.QPushButton('Deselect All')
        self.DeSelectAll.clicked.connect(self.RunsList.clearSelection)
        
        if self.orientation == 'vertical':
            if self.showDomainType:
                self.layout.addWidget(self.DomainTypeLabel,0,0)
                self.layout.addWidget(self.DomainTypeCombo,0,1)
            self.layout.addWidget(self.DomainLabel,1,0)
            self.layout.addWidget(self.DomainCombo,1,1)
            self.layout.addWidget(self.EventLabel,2,0)
            self.layout.addWidget(self.EventCombo,2,1)
            if self.showPhase:
                self.layout.addWidget(self.PhaseLabel,3,0)
                self.layout.addWidget(self.PhaseCombo,3,1)
            if self.showRun and self.runType == 'combo':
                self.layout.addWidget(self.RunLabel,4,0)
                self.layout.addWidget(self.RunCombo,4,1)
            elif self.showRun and self.runType == 'list':
                self.layout.addWidget(self.RunsLabel,5,0,1,2)
                self.layout.addWidget(self.RunsList,6,0,1,2)
                if self.multiRun:
                    self.layout.addWidget(self.SelectAll,7,0)
                    self.layout.addWidget(self.DeSelectAll,7,1)
        
        elif self.orientation == 'horizontal':
            if self.showDomainType:
                self.layout.addWidget(self.DomainTypeLabel,0,0)
                self.layout.addWidget(self.DomainTypeCombo,0,1)
            self.layout.addWidget(self.DomainLabel,0,2)
            self.layout.addWidget(self.DomainCombo,0,3)
            self.layout.addWidget(self.EventLabel,0,4)
            self.layout.addWidget(self.EventCombo,0,5)
            if self.showPhase:
                self.layout.addWidget(self.PhaseLabel,0,6)
                self.layout.addWidget(self.PhaseCombo,0,7)
            if self.showRun and self.runType == 'combo':
                self.layout.addWidget(self.RunLabel,0,8)
                self.layout.addWidget(self.RunCombo,0,9)
            elif self.showRun and self.runType == 'list':
                self.layout.addWidget(self.RunsLabel,1,0)
                self.layout.addWidget(self.RunsList,1,1,1,9)
                if self.multiRun:
                    self.layout.addWidget(self.SelectAll,2,0,1,5)
                    self.layout.addWidget(self.DeSelectAll,2,5,1,5)
                
        elif self.orientation == 'stacked':
            if self.showDomainType:
                self.layout.addWidget(self.DomainTypeLabel,0,0)
                self.layout.addWidget(self.DomainTypeCombo,0,1)
            self.layout.addWidget(self.DomainLabel,0,2)
            self.layout.addWidget(self.DomainCombo,0,3)
            self.layout.addWidget(self.EventLabel,1,0)
            self.layout.addWidget(self.EventCombo,1,1)
            if self.showPhase:
                self.layout.addWidget(self.PhaseLabel,1,2)
                self.layout.addWidget(self.PhaseCombo,1,3)
            if self.showRun and self.runType == 'combo':
                self.layout.addWidget(self.RunLabel,2,0)
                self.layout.addWidget(self.RunCombo,2,1)
            elif self.showRun and self.runType == 'list':
                self.layout.addWidget(self.RunsLabel,2,0)
                self.layout.addWidget(self.RunsList,2,1,1,3)
                if self.multiRun:
                    self.layout.addWidget(self.SelectAll,3,0,1,2)
                    self.layout.addWidget(self.DeSelectAll,3,2,1,2)
    
    def makeConnections(self):
        #Population connections
        self.DomainTypeCombo.currentIndexChanged.connect(lambda trash:self.populate_domains())
        self.DomainCombo.currentIndexChanged.connect(lambda trash:self.populate_events())
        self.EventCombo.currentIndexChanged.connect(lambda trash:self.populate_phases())
        self.PhaseCombo.currentIndexChanged.connect(lambda trash:self.populate_runs())
        self.RunCombo.currentIndexChanged.connect(lambda trash:self.get_run_path())
        
        #Reload Json connections
        self.DomainTypeCombo.activated.connect(lambda trash:self.reload_json())
        
    def reload_json(self):
        self.config = AresConfig()
        self.PathData = self.config.build_paths_for_runs(get_domaintypes=self.domaintypes,get_phases=self.phases)
        self.OutputPaths = self.config.build_paths_for_output(get_domaintypes=self.domaintypes,get_phases=self.phases)
        self.ItpPaths = self.config.build_paths_for_itp(get_domaintypes=self.domaintypes,get_phases=self.phases)
        
        self.populate_domains()
        self.populate_events()
        
    def populate_domain_types(self,**kwargs):
        reload = kwargs.get('reload',False)
        ctext = self.DomainTypeCombo.currentText()
        # self.DomainTypeCombo.blockSignals(True)
        self.DomainTypeCombo.clear()
        # self.DomainTypeCombo.blockSignals(False)
        if self.PathData:
            domaintypes = list(self.PathData.keys())
            self.DomainTypeCombo.addItems(domaintypes)
            index = self.DomainTypeCombo.findText(ctext)
            if index < 0:
                index = 0
            self.DomainTypeCombo.setCurrentIndex(index)
            
    def populate_domains(self,**kwargs):
        reload = kwargs.get('reload',False)
        ctext = self.DomainCombo.currentText()
        # self.DomainCombo.blockSignals(True)
        self.DomainCombo.clear()
        # self.DomainCombo.blockSignals(False)
        
        domaintype = self.DomainTypeCombo.currentText()
        
        if self.PathData and domaintype:
            if domaintype in self.PathData:
                domains = list(self.PathData[domaintype].keys())
                if len(domains) > 1:
                    domains = ['']+domains
                self.DomainCombo.addItems(domains)
                index = self.DomainCombo.findText(ctext)
                if index < 0:
                    index = 0
                self.DomainCombo.setCurrentIndex(index)
    
    def populate_events(self,**kwargs):
        reload = kwargs.get('reload',False)
        ctext = self.EventCombo.currentText()
        # self.EventCombo.blockSignals(True)
        self.EventCombo.clear()
        # self.EventCombo.blockSignals(False)
        
        domaintype = self.DomainTypeCombo.currentText()
        domain = self.DomainCombo.currentText()
        
        if self.PathData and domain:
            if domaintype in self.PathData and domain in self.PathData[domaintype]:
                events = list(self.PathData[domaintype][domain].keys())
                if len(events) > 1:
                    events = ['']+events
                self.EventCombo.addItems(events)
                index = self.EventCombo.findText(ctext)
                if index < 0:
                    index = 0
                self.EventCombo.setCurrentIndex(index)
    
    def populate_phases(self,**kwargs):
        reload = kwargs.get('reload',False)
        ctext = self.PhaseCombo.currentText()
        
        # self.PhaseCombo.blockSignals(True)
        self.PhaseCombo.clear()
        # self.PhaseCombo.blockSignals(False)
        
        domaintype = self.DomainTypeCombo.currentText()
        domain = self.DomainCombo.currentText()
        event = self.EventCombo.currentText()
        
        if self.PathData and event:
            if domaintype in self.PathData and domain in self.PathData[domaintype] and event in self.PathData[domaintype][domain]:
                phases = list(self.PathData[domaintype][domain][event].keys())
                if len(phases) > 1 and self.showPhase:
                    phases = ['']+phases
                elif len(phases) <= 0 and not self.showPhase:
                    phases = phases
                self.PhaseCombo.addItems(phases)
                index = self.PhaseCombo.findText(ctext)
                if index < 0:
                    index = 0
                self.PhaseCombo.setCurrentIndex(index)
    
    def populate_runs(self,**kwargs):
        reload = kwargs.get('reload',False)
        ctext = self.RunCombo.currentText()
        cselection = [str(item.text()) for item in self.RunsList.selectedItems()]
        
        # self.RunCombo.blockSignals(True)
        self.RunCombo.clear()
        # self.RunCombo.blockSignals(False)
        # self.RunsList.blockSignals(True)
        self.RunsList.clear()
        # self.RunsList.blockSignals(False)
        
        domaintype = self.DomainTypeCombo.currentText()
        domain = self.DomainCombo.currentText()
        event = self.EventCombo.currentText()
        phase = self.PhaseCombo.currentText()
        
        if self.PathData and phase:
            if domaintype in self.PathData and domain in self.PathData[domaintype] and event in self.PathData[domaintype][domain] and phase in self.PathData[domaintype][domain][event]:
                if domaintype == 'Ground Test':
                    runs = ['']+self.getRuns(self.PathData[domaintype][domain][event][phase])
                elif domaintype == 'MAT':
                    runs = ['']+self.getMATRuns(self.PathData[domaintype][domain][event][phase])
                else:
                    runs = ['']+self.getGenericRuns(self.PathData[domaintype][domain][event][phase])
                self.RunCombo.addItems(runs)
                runs.pop(0)
                self.RunsList.addItems(runs)
                
                index = self.RunCombo.findText(ctext)
                if index < 0:
                    index = 0
                index = 0 #WHY?
                
                self.RunCombo.setCurrentIndex(index)
                
                for i in range(self.RunsList.count()):
                    item = self.RunsList.item(i)
                    if item.text() in cselection:
                        item.setSelected(True)
    
    def getRuns(self,basepath):
        runs = []
        runs = sorted([path for path in os.listdir(basepath) if re.search('\d{3}.\d+',path) and os.path.isdir(os.path.join(basepath,path))])
        return runs
    
    def getGenericRuns(self,basepath):
        dirs = os.listdir(basepath)
        dirs = [x for x in dirs if os.path.isdir(os.path.join(basepath,x))]
        return sorted(dirs)
    
    def getMATRuns(self,basepath):
        dirs = os.listdir(basepath)
        dirs = [x for x in dirs if os.path.isdir(os.path.join(basepath,x))]
        return sorted(dirs)
    
    def get_runs_from_list(self,**kwargs):
        emit = kwargs.get('emit',True)
        selectedRuns = [str(item.text()) for item in self.RunsList.selectedItems()]
        if selectedRuns:
            domaintype = self.DomainTypeCombo.currentText()
            domain = self.DomainCombo.currentText()
            event = self.EventCombo.currentText()
            phase = self.PhaseCombo.currentText()
            if domaintype and domain and event and phase:
                basepath = self.PathData[domaintype][domain][event][phase]
                runpaths = list(map(lambda x:os.path.join(basepath,x),selectedRuns))
            if emit:
                self.RunPathsChanged.emit(runpaths)
            return runpaths
        else:
            return []
    
    def get_run_path(self,**kwargs):
        emit = kwargs.get('emit',True)
        run = kwargs.get('run','')
        domaintype = self.DomainTypeCombo.currentText()
        domain = self.DomainCombo.currentText()
        event = self.EventCombo.currentText()
        phase = self.PhaseCombo.currentText()
        
        if not run:
            run = self.RunCombo.currentText()
        
        if domaintype and domain and event and phase and run:
            basepath = self.PathData[domaintype][domain][event][phase]
            runpath = os.path.join(basepath,run)
        else:
            runpath = ''
        if emit:
            self.RunPathChanged.emit(runpath)
        return runpath
    
    def get_execution_path(self,**kwargs):
        emit = kwargs.get('emit',True)
        domaintype = self.DomainTypeCombo.currentText()
        domain = self.DomainCombo.currentText()
        event = self.EventCombo.currentText()
        phase = self.PhaseCombo.currentText()
        
        if domaintype and domain and event and phase:
            execpath = self.PathData[domaintype][domain][event][phase]
        else:
            execpath = ''
        if emit:
            self.ExecutionPathChanged.emit(execpath)
        return execpath
        
    def get_output_path(self,**kwargs):
        emit = kwargs.get('emit',True)
        domaintype = self.DomainTypeCombo.currentText()
        domain = self.DomainCombo.currentText()
        event = self.EventCombo.currentText()
        phase = self.PhaseCombo.currentText()
        
        if domaintype and domain and event and phase:
            outputpath = self.OutputPaths[domaintype][domain][event][phase]
        else:
            outputpath = ''
        if emit:
            self.OutputPathChanged.emit(outputpath)
        return outputpath
    
    def get_itp_path(self,**kwargs):
        emit = kwargs.get('emit',True)
        domaintype = self.DomainTypeCombo.currentText()
        domain = self.DomainCombo.currentText()
        event = self.EventCombo.currentText()
        
        if domaintype and domain and event:
            itppath = self.ItpPaths[domaintype][domain][event]
        else:
            itppath = ''
        if emit:
            self.ItpPathChanged.emit(itppath)
        return itppath
                
            
