# -*- coding: utf-8 -*-
"""
Created on Fri Mar 27 11:05:05 2020

@author: cjmar
"""

import os
import sys

import matplotlib.pyplot as plt
import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import PyQt5.QtWidgets as Widgets
import PyQt5.QtGui as Gui
import PyQt5.QtCore as Core
from PyQt5 import uic
from collections import OrderedDict
import numpy as np
import struct
import binascii
from six import string_types
import pandas as pd
plt.rcParams['toolbar'] = 'toolmanager'


if not hasattr(sys, 'frozen'):
    RELATIVE_LIB_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
    if __name__ == '__main__':
        sys.path.append(RELATIVE_LIB_PATH)
        sys.path.pop(0)
else:
    RELATIVE_LIB_PATH = os.path.dirname(os.path.dirname(sys.executable))

from PlotH5.mpltools import mplDefaults as mpld
from PlotH5.mpltools import mplUtils as mplu
from PlotH5.mpltools.toolbarUtils import add_Tool
from PlotH5 import Plotterator
resource_path = os.path.join(RELATIVE_LIB_PATH,'PlotH5','mpltools','toolbarIcons')

class PlotWidget(Widgets.QWidget):
    def __init__(self,parent=None,data=pd.DataFrame(),**kwargs):
        super(PlotWidget,self).__init__(parent)
        uic.loadUi(os.path.join(RELATIVE_LIB_PATH,'PlotH5','mpltools','WidgetUIs','PlotWidget.ui'),self)
        
        self.parent = parent
        self.data = data
        self.options_dialog = None
        
        self.edit = kwargs.get('edit',False)
        self.init_toolbar()
        
        self.process_kwargs()
        self.setup_init_plot_canvas()
        
    def init_toolbar(self):
        self.toolbar = Widgets.QToolBar()
        self.ToolbarLayout.addWidget(self.toolbar)
        if self.edit:
            self.edit_action = Widgets.QToolButton(self)
            self.edit_action.setIcon(Gui.QIcon(os.path.join(resource_path,'options.jpg')))
            self.edit_action.setStatusTip('Show/Hide Options Window')
            self.edit_action.setCheckable(True)
            self.edit_action.toggled.connect(self.show_options)
            self.toolbar.addWidget(self.edit_action)
            
    def show_options(self,state):
        if not self.options_dialog:
            self.options_dialog = EditOptionsDialog(parent=self)
        if state:
            self.options_dialog.show()
        else:
            self.edit_action.setChecked(False)
            self.options_dialog.hide()
        
    def setup_init_plot_canvas(self):
        pltr = Plotterator.Plotter(classy='')
        ax = pltr.add_subplot()
        pltr.plot([],[],axid=ax)
        self.Plot_All(pltr)
        
    def process_kwargs(self):
        if self.edit:
            pass
    
    def Plot_All(self,plo):
        #plo is the Plotterator object
        fig = plo.createPlot('',CANVAS=True)
        figcanvas = FigureCanvas(fig)
        toolbar = NavigationToolbar(figcanvas,None)
        for i in reversed(range(self.PlotCanvasLayout.count())): 
            self.PlotCanvasLayout.itemAt(i).widget().deleteLater()
        self.PlotCanvasLayout.addWidget(toolbar)
        self.PlotCanvasLayout.addWidget(figcanvas)            
    

class EditOptionsDialog(Widgets.QDialog):
    def __init__(self,parent=None,**kwargs):
        super(EditOptionsDialog,self).__init__(parent)
        uic.loadUi(os.path.join(RELATIVE_LIB_PATH,'PlotH5','mpltools','WidgetUIs','PlotWidgetEditOptions.ui'),self)
        self.parent = parent
        #Assuming parent data is a dataframe
        self.data = parent.data
        
        self.populate_edit_options()
        self.manage_global_options()
        
        self.makeConnections()
        
    def makeConnections(self):
        self.PlotTypeCombo.currentIndexChanged.connect(self.manage_global_options)
        #Line options
        self.LineYAxisHeaders.itemSelectionChanged.connect(self.Plot)
        self.LineXAxisHeader.currentIndexChanged.connect(self.Plot)
        
    def manage_global_options(self):
        plctext = self.PlotTypeCombo.currentText()
        if plctext.startswith('3D'):
            self.ZLabel.show()
            self.ZLabelLine.show()
        else:
            self.ZLabel.hide()
            self.ZLabelLine.hide()
    
    def Plot(self):
        ptctext = self.PlotTypeCombo.currentText()
        classy = self.ClassificationLine.text()
        title = self.TitleLine.text()
        xlabel = self.XLabelLine.text()
        ylabel = self.YLabelLine.text()
        zlabel = self.ZLabelLine.text()
        pltr = Plotterator.Plotter(classy=classy,title=title)
        if 'cartopy' not in ptctext and '3D' not in ptctext:
            pax = pltr.add_subplot()
        pltr.parseCommand(pax,'set_ylabel',[[ylabel]])
        pltr.parseCommand(pax,'set_xlabel',[[xlabel]])
        
        #Need to loop over all the things to make sure i get all the plots
        if ptctext == 'Line Plot':
            #Sort data first
            xaxis = self.LineXAxisHeader.currentText()
            cbu = [se.text() for se in self.LineCodeByUniqueList.selectedItems()]
            ys = [se.text() for se in self.LineYAxisHeaders.selectedItems()]
            if xaxis and ys:
                self.data.sort_values(xaxis,inplace=True)
                for y in ys:
                    pltr.plot(self.data[xaxis],self.data[y],axid=pax)
            else:
                return
        self.parent.Plot_All(pltr)
    
    def populate_edit_options(self):
        ptctext = self.PlotTypeCombo.currentText()
        if ptctext == 'Line Plot':
            headers = list(self.data)
            for header in headers:
                if self.data[header].dtype.kind not in ['S','O','U']:
                    self.LineYAxisHeaders.addItem(header)
                    self.LineXAxisHeader.addItem(header)
                    self.LineCodeByUniqueList.addItem(header)
            self.LineXAxisHeader.setCurrentIndex(-1)
            
    def closeEvent(self,event):
        self.parent.show_options(False)


if __name__ == '__main__':
    dic = {'this':np.random.randint(0,500,50000),'that':np.random.randint(0,500,50000)}
    data = pd.DataFrame(dic)
    app = Widgets.QApplication(sys.argv)
    widget = PlotWidget(None,data,edit=True)
    widget.show()
    app.exec_()
    sys.exit(0)