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
import numpy as np
from six import string_types
plt.rcParams['toolbar'] = 'toolmanager'

if not hasattr(sys, 'frozen'):
    RELATIVE_LIB_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
    if __name__ == '__main__':
        sys.path.append(RELATIVE_LIB_PATH)
        sys.path.pop(0)
else:
    RELATIVE_LIB_PATH = os.path.dirname(sys.executable)

from PlotH5.mpltools import mplDefaults as mpld
from PlotH5.mpltools import mplUtils as mplu


class edit_subplot_options(Widgets.QDialog):
    def __init__(self,fig,parent=None):
        super(edit_subplot_options,self).__init__(parent)
        uic.loadUi(os.path.join(RELATIVE_LIB_PATH,'PlotH5','mpltools','toolbarUIs','subplotoptions.ui'),self)
        
        self.parent = parent
        self.setWindowTitle('Subplot Options')
        self.fig = fig
        self.axlookup = {}
        self.special_options()
        self.makeConnections()
        self.populate_axes_combo()
        self.populate_options(0)
        
    def makeConnections(self):
        self.AxisCombo.currentIndexChanged.connect(self.populate_options)
        self.AspectCombo.currentIndexChanged.connect(lambda:self.update_aspect())
        self.XUpperLim.textChanged.connect(lambda trash:self.update_limits('x'))
        self.XLowerLim.textChanged.connect(lambda trash:self.update_limits('x'))
        self.YUpperLim.textChanged.connect(lambda trash:self.update_limits('y'))
        self.YLowerLim.textChanged.connect(lambda trash:self.update_limits('y'))
        self.XLog.toggled.connect(lambda trash:self.update_scale('x'))
        self.XLinear.toggled.connect(lambda trash:self.update_scale('x'))
        self.XSymlog.toggled.connect(lambda trash:self.update_scale('x'))
        self.XLogit.toggled.connect(lambda trash:self.update_scale('x'))
        self.YLog.toggled.connect(lambda trash:self.update_scale('y'))
        self.YLinear.toggled.connect(lambda trash:self.update_scale('y'))
        self.YSymlog.toggled.connect(lambda trash:self.update_scale('y'))
        self.YLogit.toggled.connect(lambda trash:self.update_scale('y'))
        self.AxisFacecolor.currentIndexChanged.connect(lambda trash:self.update_facecolor('ax'))
        self.FigureFacecolor.currentIndexChanged.connect(lambda trash:self.update_facecolor('fig'))
    
    def special_options(self):
        dval = Gui.QDoubleValidator()
        dval.setNotation(0)
        self.XUpperLim.setValidator(dval)
        self.XLowerLim.setValidator(dval)
        self.YUpperLim.setValidator(dval)
        self.YLowerLim.setValidator(dval)
    
    def populate_axes_combo(self):
        self.axlist = []
        axes = self.fig.axes
        for ax in axes:
            props = ax.properties()
            if isinstance(props['children'][0],matplotlib.collections.QuadMesh):
                continue
            else:
                if ax.get_title():
                    self.axlookup[ax] = f'{ax.get_title()}'
                elif ax.get_ylabel() and ax.get_xlabel():
                    self.axlookup[ax] = f'{ax.get_ylabel()} vs. {ax.get_xlabel()}'
                else:
                    y = ax.properties()
                    self.axlookup[ax] = str(mplu.getSpan(y['subplotspec'], y['geometry']))
                self.axlist.append(ax)
        for i,ax in enumerate(self.axlist):
            if self.axlookup[ax]:
                self.AxisCombo.addItem(self.axlookup[ax])
            else:
                self.AxisCombo.addItem(str(i))
    
    def Signals(self,state):
        self.AxisFacecolor.blockSignals(state)
        self.FigureFacecolor.blockSignals(state)
        self.XUpperLim.blockSignals(state)
        self.XLowerLim.blockSignals(state)
        self.YUpperLim.blockSignals(state)
        self.YLowerLim.blockSignals(state)
        self.AspectCombo.blockSignals(state)
        
    def populate_aspect(self):
        self.AspectCombo.clear()
        aspect_items = ['auto','equal']
        aspect = self.ax.get_aspect()
        if aspect not in aspect_items:
            aspect_items.append(str(aspect))
        self.AspectCombo.addItems(aspect_items)
        index = self.AspectCombo.findText(aspect)
        self.AspectCombo.setCurrentIndex(index)
        
    def populate_background_colors(self):
        self.AxisFacecolor.clear()
        self.FigureFacecolor.clear()
        colors = list(mpld.NametoRGB.keys())
        currentafc = self.ax.get_facecolor()
        if isinstance(currentafc,tuple):
            if len(currentafc) == 4:
                currentafc = currentafc[:-1]
            currentafc = mplu.get_closest_name_rgb(currentafc)
        elif isinstance(currentafc,string_types) and '#' not in currentafc:
            currentafc = mplu.get_closest_name_name(currentafc)
        elif isinstance(currentafc,string_types) and '#' in currentafc:
            currentafc = mplu.get_closest_name_rgb(mplu.convert_hex_to_rgb(currentafc))
        else:
            currentafc = 'w'
        currentffc = self.fig.get_facecolor()
        if isinstance(currentffc,tuple):
            if len(currentffc) == 4:
                currentffc = currentffc[:-1]
            currentffc = mplu.get_closest_name_rgb(currentffc)
        elif isinstance(currentffc,string_types) and '#' not in currentffc:
            currentffc = mplu.get_closest_name_name(currentffc)
        elif isinstance(currentffc,string_types) and '#' in currentffc:
            currentffc = mplu.get_closest_name_rgb(mplu.convert_hex_to_rgb(currentffc))
        else:
            currentffc = 'w'
        
        self.AxisFacecolor.addItems(colors)
        self.FigureFacecolor.addItems(colors)
        
        index = self.AxisFacecolor.findText(currentafc)
        self.AxisFacecolor.setCurrentIndex(index)
        index = self.FigureFacecolor.findText(currentffc)
        self.FigureFacecolor.setCurrentIndex(index)
        
    def set_scale_group(self):
        xscale = self.ax.get_xscale()
        yscale = self.ax.get_yscale()
        if xscale == 'linear':
            self.XLinear.setChecked(True)
        elif xscale == 'log':
            self.XLog.setChecked(True)
        elif xscale == 'symlog':
            self.XSymlog.setChecked(True)
        else:
            self.XLogit.setChecked(True)
        if yscale == 'linear':
            self.YLinear.setChecked(True)
        elif yscale == 'log':
            self.YLog.setChecked(True)
        elif yscale == 'symlog':
            self.YSymlog.setChecked(True)
        else:
            self.YLogit.setChecked(True)
    
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
            self.populate_background_colors()
            self.set_scale_group()
            self.populate_aspect()
        self.Signals(False)
        
    def update_aspect(self):
        ctext = self.AspectCombo.currentText()
        try:
            val = float(ctext)
        except:
            val = ctext
        self.ax.set_aspect(val)
            
    def update_limits(self,axis):
        if axis in ['x','X']:
            ux = self.XUpperLim.text()
            lx = self.XLowerLim.text()
            if ux and lx and self.ax:
                try:
                    self.ax.set_xlim(float(lx),float(ux))
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

    def update_facecolor(self,obj):
        if obj == 'fig':
            ctext = self.FigureFacecolor.currentText()
            if ctext:
                rgb = mpld.NametoRGB[ctext]
                self.fig.set_facecolor(rgb)
            else:
                self.fig.set_facecolor((1.0,1.0,1.0,1.0))
        elif obj == 'ax':
            ctext = self.AxisFacecolor.currentText()
            if ctext:
                rgb = mpld.NametoRGB[ctext]
                self.ax.set_facecolor(rgb)
            else:
                self.ax.set_facecolor((1.0,1.0,1.0,1.0))
    
    def update_scale(self,axis):
        if axis == 'x':
            if self.XLog.isChecked():
                self.ax.set_xscale('log')
            elif self.XSymlog.isChecked():
                self.ax.set_xscale('symlog')
            elif self.XLogit.isChecked():
                self.ax.set_xscale('logit')
            else:
                self.ax.set_xscale('linear')
        elif axis == 'y':
            if self.YLog.isChecked():
                self.ax.set_yscale('log')
            elif self.YSymlog.isChecked():
                self.ax.set_yscale('symlog')
            elif self.YLogit.isChecked():
                self.ax.set_yscale('logit')
            else:
                self.ax.set_yscale('linear')
                
def edit_subplots(*args,**kwargs):
    dialog = edit_subplot_options(*args,**kwargs)
    dialog.exec_()