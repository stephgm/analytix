# -*- coding: utf-8 -*-
"""
Created on Wed Mar 25 15:55:45 2020

@author: cjmar
"""


import os
import sys

import matplotlib.pyplot as plt
import matplotlib
import PyQt5.QtWidgets as Widgets
import PyQt5.QtGui as Gui
import PyQt5.QtCore as Core
from PyQt5 import uic
from collections import OrderedDict
import numpy as np
import struct
import binascii
from six import string_types
plt.rcParams['toolbar'] = 'toolmanager'

if not hasattr(sys, 'frozen'):
    RELATIVE_LIB_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
    if __name__ == '__main__':
        sys.path.append(RELATIVE_LIB_PATH)
        sys.path.pop(0)
else:
    RELATIVE_LIB_PATH = os.path.dirname(sys.executable)

class edit_subplot_options(Widgets.QDialog):
    def __init__(self,fig,parent=None):
        super(edit_subplot_options,self).__init__(parent)
        uic.loadUi(os.path.join(RELATIVE_LIB_PATH,'PlotH5','mpltools','toolbarUIs','subplotoptions.ui'),self)
        
        self.parent = parent
        self.fig = fig
        self.special_options()
        self.makeConnections()
        self.populate_axes_combo()
        self.populate_options(0)
        
    def makeConnections(self):
        self.AxisCombo.currentIndexChanged.connect(self.populate_options)
        self.XUpperLim.textChanged.connect(lambda trash:self.update_limits('x'))
        self.XLowerLim.textChanged.connect(lambda trash:self.update_limits('x'))
        self.YUpperLim.textChanged.connect(lambda trash:self.update_limits('y'))
        self.YLowerLim.textChanged.connect(lambda trash:self.update_limits('y'))
    
    def special_options(self):
        self.XUpperLim.setValidator(Gui.QDoubleValidator())
        self.XLowerLim.setValidator(Gui.QDoubleValidator())
        self.YUpperLim.setValidator(Gui.QDoubleValidator())
        self.YLowerLim.setValidator(Gui.QDoubleValidator())
    
    def populate_axes_combo(self):
        self.axlist = []
        axes = self.fig.axes
        for ax in axes:
            props = ax.properties()
            if isinstance(props['children'][0],matplotlib.collections.QuadMesh):
                continue
            else:
                self.axlist.append(ax)
        for i in range(len(self.axlist)):
            self.AxisCombo.addItem(str(i))
    
    def Signals(self,state):
        self.XUpperLim.blockSignals(state)
        self.XLowerLim.blockSignals(state)
        self.YUpperLim.blockSignals(state)
        self.YLowerLim.blockSignals(state)
    
    def populate_options(self,index):
        self.Signals(True)
        if index < len(self.axlist):
            self.ax = self.axlist[index]
            xlims = self.ax.get_xlim()
            ylims = self.ax.get_ylim()
            self.XUpperLim.setText(str(xlims[1]))
            self.XLowerLim.setText(str(xlims[0]))
            self.YUpperLim.setText(str(ylims[1]))
            self.YLowerLim.setText(str(ylims[0]))
        self.Signals(False)
        
    def update_limits(self,axis):
        if axis in ['x','X']:
            ux = self.XUpperLim.text()
            lx = self.XLowerLim.text()
            if ux and lx and self.ax:
                try:
                    oldax = self.ax
                    self.ax.set_xlim(float(lx),float(ux))
                    print(lx,ux)
                    print(self.ax.get_xlim())
                    print(self.ax==oldax)
                except:
                    pass
        elif axis in ['y','Y'] and self.ax:
            uy = self.YUpperLim.text()
            ly = self.YLowerLim.text()
            if uy and ly:
                try:
                    self.ax.set_ylim(float(ly),float(uy))
                except:
                    pass
                
def edit_subplots(*args,**kwargs):
    dialog = edit_subplot_options(*args,**kwargs)
    dialog.exec_()