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


class PlotWidget(Widgets.QWidget):
    def __init__(self,parent=None,**kwargs):
        super(PlotWidget,self).__init__(parent)
        uic.loadUi(os.path.join(RELATIVE_LIB_PATH,'PlotH5','mpltools','WidgetUIs','PlotWidget.ui'),self)
        
        self.parent = parent
        
        self.edit = kwargs.get('edit',False)
        
        self.process_kwargs()
        self.setup_init_plot_canvas()
        
    def setup_init_plot_canvas(self):
        pltr = Plotterator.Plotter(classy='')
        ax = pltr.add_subplot()
        pltr.plot([],[],axid=ax)
        fig = pltr.createPlot('', CANVAS=True)
        figcanvas = FigureCanvas(fig)
        toolbar = NavigationToolbar(figcanvas,None)
        self.PlotCanvasLayout.addWidget(toolbar)
        self.PlotCanvasLayout.addWidget(figcanvas)
        
    def process_kwargs(self):
        if not self.edit:
            self.EditWidget.hide()
            
    
            
        


if __name__ == '__main__':
    app = Widgets.QApplication(sys.argv)
    widget = PlotWidget(edit=True)
    widget.show()
    app.exec_()
    sys.exit(0)