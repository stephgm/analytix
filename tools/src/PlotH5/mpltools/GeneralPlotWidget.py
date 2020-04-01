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
        tbar = add_Tool(fig,['Editor','SubplotOptions'],get_toolbar=True)
        figcanvas = FigureCanvas(fig)
        for i in reversed(range(self.PlotCanvasLayout.count())): 
            self.PlotCanvasLayout.itemAt(i).widget().deleteLater()
        self.PlotCanvasLayout.addWidget(tbar)
        self.PlotCanvasLayout.addWidget(figcanvas)
    

class EditOptionsDialog(Widgets.QDialog):
    def __init__(self,parent=None,**kwargs):
        super(EditOptionsDialog,self).__init__(parent)
        uic.loadUi(os.path.join(RELATIVE_LIB_PATH,'PlotH5','mpltools','WidgetUIs','PlotWidgetEditOptions.ui'),self)
        self.parent = parent
        #Assuming parent data is a dataframe
        self.data = parent.data
        
        self.codebydict = {}
        
        self.populate_edit_options()
        self.manage_global_options()
        
        self.makeConnections()
        
    def makeConnections(self):
        self.PlotTypeCombo.currentIndexChanged.connect(self.manage_global_options)
        #Line options
        self.LineYAxisHeaders.itemSelectionChanged.connect(self.Plot)
        self.LineYAxisHeaders.itemSelectionChanged.connect(lambda:self.populate_code_table(self.LineYAxisHeaders,self.LineCodeByTable))
        self.LineXAxisHeader.currentIndexChanged.connect(self.Plot)
        self.LineSearchBar.textChanged.connect(lambda txt:self.Search(txt,self.LineYAxisHeaders))
        #Scatter options
        self.ScatterYAxisHeaders.itemSelectionChanged.connect(self.Plot)
        self.ScatterYAxisHeaders.itemSelectionChanged.connect(lambda:self.populate_code_table(self.ScatterYAxisHeaders,self.ScatterCodeByTable))
        self.ScatterXAxisHeader.currentIndexChanged.connect(self.Plot)
        self.ScatterSearchBar.textChanged.connect(lambda txt:self.Search(txt,self.ScatterYAxisHeaders))
        #Pie Options
        self.PieXAxisHeader.currentIndexChanged.connect(lambda trash:self.set_max_bins(self.PieXAxisHeader,self.PieBins))
        self.PieXAxisHeader.currentIndexChanged.connect(self.Plot)
        self.PieBins.valueChanged.connect(lambda trash:self.Plot())
        #Timeline Options
        self.TimelineYAxisHeaders.itemSelectionChanged.connect(self.Plot)
        self.TimelineYAxisHeaders.itemSelectionChanged.connect(lambda:self.populate_code_table(self.TimelineYAxisHeaders,self.TimelineCodeByTable))
        self.TimelineXAxisHeader.currentIndexChanged.connect(self.Plot)
        self.TimelineSearchBar.textChanged.connect(lambda txt:self.Search(txt,self.TimelineYAxisHeaders))
        #Histogram Options
        self.HistogramXAxisHeader.currentIndexChanged.connect(lambda trash:self.set_max_bins(self.HistogramXAxisHeader,self.HistogramBins))
        self.HistogramXAxisHeader.currentIndexChanged.connect(self.Plot)
        self.HistogramBins.valueChanged.connect(lambda trash:self.Plot())
        self.HistogramNormChk.toggled.connect(lambda trash:self.Plot())
        #Bar Chart Options
        self.BarChartYAxisHeaders.itemSelectionChanged.connect(self.Plot)
        self.BarChartXAxisHeader.currentIndexChanged.connect(self.Plot)
        
    def Search(self,txt,widget):
        for i in range(widget.count()):
            widget.item(i).setHidden(txt.lower() not in widget.item(i).text().lower())
            
    def set_max_bins(self,combo,binwidget):
        txt = combo.currentText()
        curval = binwidget.value()
        if txt:
            num_bins = len(pd.unique(self.data[txt]))
        else:
            num_bins = 1000
        if curval > num_bins:
            cuval = num_bins
        binwidget.setMaximum(num_bins)
        binwidget.setValue(curval)
            
    
    def populate_code_table(self,listwidget,tablewidget):
        #Table columns:
            #Y header:::Source Header:::Type:::Cmap:::Colorbarlabel
        se = [i.text() for i in listwidget.selectedItems()]
        al = [''] + [str(listwidget.item(i).text()) for i in range(listwidget.count())]
        cmaps = mpld.cmaps
        former = []
        for i in range(tablewidget.rowCount()-1,-1,-1):
            if tablewidget.itemAt(i,0).text() not in se:
                tablewidget.removeRow(i)
            else:
                former.append(tablewidget.itemAt(i,0).text())
        self.codebydict[listwidget] = {}
        for header in se:
            if header not in former:
                self.codebydict[listwidget][header] = dict(source=None,mtype=None,cmap=None)
                
                source_combo = Widgets.QComboBox()
                source_combo.addItems(al)
                source_combo.setCurrentIndex(0)
                source_combo.currentIndexChanged.connect(self.Plot)
                source_combo.wheelEvent = lambda trash:None
                
                type_combo = Widgets.QComboBox()
                if listwidget.objectName().startswith('Line'):
                    type_combo.addItems(['Color Code'])
                else:
                    type_combo.addItems(['Colorbar','Color Code'])
                type_combo.setCurrentIndex(0)
                type_combo.currentIndexChanged.connect(lambda trash,lw=listwidget,tw=tablewidget:self.handle_colorbar_code_widgets(lw,tw))
                type_combo.currentIndexChanged.connect(self.Plot)
                type_combo.wheelEvent = lambda trash:None
                
                cmap_combo = Widgets.QComboBox()
                cmap_combo.addItems(cmaps)
                cmap_combo.setCurrentIndex(0)
                cmap_combo.currentIndexChanged.connect(self.Plot)
                cmap_combo.wheelEvent = lambda trash:None
                
                self.codebydict[listwidget][header]['source']=source_combo
                self.codebydict[listwidget][header]['mtype']=type_combo
                self.codebydict[listwidget][header]['cmap']=cmap_combo
                rowPosition = tablewidget.rowCount()
                tablewidget.insertRow(rowPosition)
                headeritem = Widgets.QTableWidgetItem(header)
                headeritem.setFlags(Core.Qt.ItemIsEnabled)
                cbarheaderitem = Widgets.QTableWidgetItem('')
                tablewidget.setItem(rowPosition , 0, headeritem)
                tablewidget.setCellWidget(rowPosition, 1, source_combo)
                tablewidget.setCellWidget(rowPosition, 2, type_combo)
                tablewidget.setCellWidget(rowPosition, 3, cmap_combo)
                tablewidget.setItem(rowPosition, 4, cbarheaderitem)
                self.handle_colorbar_code_widgets(listwidget,tablewidget)
                
            
    def get_code_dict(self,listwidget,tablewidget):
        cdict = {}
        for i in range(tablewidget.rowCount()):
            for header in self.codebydict[listwidget]:
                if self.codebydict[listwidget][header]['source'].currentText():
                    cdict[header] = dict(source='',mtype='',cmap=None,cbarlabel=None)
                    source = self.codebydict[listwidget][header]['source'].currentText()
                    mtype = self.codebydict[listwidget][header]['mtype'].currentText()
                    cmap = self.codebydict[listwidget][header]['cmap'].currentText()
                    cbarlabel = tablewidget.itemAt(i,4).text()
                    cdict[header]['source']=source
                    cdict[header]['mtype']=mtype
                    cdict[header]['cmap']=cmap
                    cdict[header]['cbarlabel']=cbarlabel
        return cdict
            
        
    def manage_global_options(self):
        plctext = self.PlotTypeCombo.currentText()
        if plctext.startswith('3D'):
            self.ZLabel.show()
            self.ZLabelLine.show()
        else:
            self.ZLabel.hide()
            self.ZLabelLine.hide()
            
    def handle_colorbar_code_widgets(self,listwidget,tablewidget):
        for i in range(tablewidget.rowCount()):
            for header in self.codebydict[listwidget]:
                if self.codebydict[listwidget][header]['mtype'].currentText() == 'Colorbar':
                    cbarlabel = tablewidget.itemAt(i,4)
                    cbarlabel.setFlags(Core.Qt.ItemIsEditable | Core.Qt.ItemIsEnabled)
                    self.codebydict[listwidget][header]['cmap'].setEnabled(True)
                else:
                    cbarlabel = tablewidget.itemAt(i,4)
                    cbarlabel.setFlags(Core.Qt.ItemIsEnabled)
                    self.codebydict[listwidget][header]['cmap'].setEnabled(False)
                    
    def color_code(self,source,xaxis,yaxis,pltr,pax,ptype):
        uniques = pd.unique(self.data[source])
        for unique in uniques:
            xdata = self.data[self.data[source]==unique][xaxis]
            ydata = self.data[self.data[source]==unique][yaxis]
            if ptype == 'Line Plot':
                pltr.plot(xdata,ydata,axid=pax,marker='o')
            elif ptype == 'Scatter':
                pltr.scatter(xdata,ydata,axid=pax,marker='o')
            elif ptype == 'Timeline':
                pltr.scatter(xdata,sorted(ydata.astype(str)),axid=pax,marker='o')
                
    def colorbar_plot(self,source,xaxis,yaxis,pltr,pax,ptype,cbarlabel,cmap):
        xdata = self.data[xaxis]
        ydata = self.data[yaxis]
        colors = self.data[source]
        if ptype == 'Scatter':
            pltr.scatter(xdata,ydata,c=colors,cmap=cmap,axid=pax)
        elif ptype == 'Timeline':
            pltr.scatter(xdata,sorted(ydata.astype(str)),c=colors,cmap=cmap,axid=pax)
        
        pltr.add_colorbar(pax,cmap,cbarlabel,np.array([max(colors),min(colors)]))
        
    def make_pie_chart(self,xaxis,pltr,pax,bins):
        xdata = self.data[xaxis]
        xdata = pd.cut(xdata,bins)
        cmap = plt.cm.jet
        colors = cmap(np.linspace(0,1,bins))
        pievals = xdata.value_counts().sort_index()
        legend = map(str,pievals.index.tolist())
        pltr.pie(pievals,autopct='%.2f%%',colors=colors,axid=pax)
        pltr.parseCommand(pax,'set_aspect',[['equal']])
    
    def make_histogram(self,xaxis,pltr,pax,bins):
        xdata = self.data[xaxis]
        pltr.hist(xdata,bins,axid=pax,normed=self.HistogramNormChk.isChecked())
        if self.HistogramNormChk.isChecked():
            pass
            #Dunno how to set percent formatter for y axis in plotterator..
            # pltr.parseCommand(pax,'yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(100))',[[]])
    
    def Plot(self):
        AllItems = [self.PlotTypeCombo.itemText(i) for i in range(self.PlotTypeCombo.count())]
        classy = self.ClassificationLine.text()
        title = self.TitleLine.text()
        xlabel = self.XLabelLine.text()
        ylabel = self.YLabelLine.text()
        zlabel = self.ZLabelLine.text()
        pltr = Plotterator.Plotter(classy=classy,title=title)
        # if 'cartopy' not in ptctext and '3D' not in ptctext:
        pax = pltr.add_subplot((0,0),1,2)
        # mapax = pltr.add_subplot((1,0),mapplot=True)
        # tdpax = pltr.add_subplot((1,1),threeD=True)
        pltr.parseCommand(pax,'set_ylabel',[[ylabel]])
        pltr.parseCommand(pax,'set_xlabel',[[xlabel]])
        
        #Need to loop over all the things to make sure i get all the plots
        for ptctext in AllItems:
            if ptctext == 'Line Plot':
                #Sort data first
                xaxis = self.LineXAxisHeader.currentText()
                ys = [se.text() for se in self.LineYAxisHeaders.selectedItems()]
                cdict = self.get_code_dict(self.LineYAxisHeaders,self.LineCodeByTable)
                if xaxis and ys:
                    self.data.sort_values(xaxis,inplace=True)
                    for y in ys:
                        if cdict and y in cdict:
                            source = cdict[y]['source']
                            mtype = cdict[y]['mtype']
                            if mtype == 'Color Code':
                                self.color_code(source,xaxis,y,pltr,pax,ptctext)
                            else:
                                pass
                        else:
                            pltr.plot(self.data[xaxis],self.data[y],axid=pax,marker='o')
                else:
                    continue
            elif ptctext == 'Scatter':
                #Sort data first
                xaxis = self.ScatterXAxisHeader.currentText()
                ys = [se.text() for se in self.ScatterYAxisHeaders.selectedItems()]
                cdict = self.get_code_dict(self.ScatterYAxisHeaders,self.ScatterCodeByTable)
                if xaxis and ys:
                    self.data.sort_values(xaxis,inplace=True)
                    for y in ys:
                        if cdict and y in cdict:
                            source = cdict[y]['source']
                            mtype = cdict[y]['mtype']
                            if mtype == 'Color Code':
                                self.color_code(source,xaxis,y,pltr,pax,ptctext)
                            elif mtype == 'Colorbar':
                                self.colorbar_plot(source,xaxis,y,pltr,pax,ptctext,cdict[y]['cbarlabel'],cdict[y]['cmap'])
                        else:
                            pltr.scatter(self.data[xaxis],self.data[y],axid=pax,marker='o')
            elif ptctext == 'Pie':
                xaxis = self.PieXAxisHeader.currentText()
                if xaxis:
                    self.data.sort_values(xaxis,inplace=True)
                    bins = self.PieBins.value()
                    self.make_pie_chart(xaxis,pltr,pax,bins)
            elif ptctext == 'Timeline':
                xaxis = self.TimelineXAxisHeader.currentText()
                ys = [se.text() for se in self.TimelineYAxisHeaders.selectedItems()]
                cdict = self.get_code_dict(self.TimelineYAxisHeaders,self.TimelineCodeByTable)
                if xaxis and ys:
                    #Sort by Y?
                    self.data.sort_values(xaxis,inplace=True)
                    for y in ys:
                        # self.data.sort_values(y,inplace=True)
                        if cdict and y in cdict:
                            source = cdict[y]['source']
                            mtype = cdict[y]['mtype']
                            if mtype == 'Color Code':
                                self.color_code(source,xaxis,y,pltr,pax,ptctext)
                            elif mtype == 'Colorbar':
                                self.colorbar_plot(source,xaxis,y,pltr,pax,ptctext,cdict[y]['cbarlabel'],cdict[y]['cmap'])
                        else:
                            pltr.scatter(self.data[xaxis],sorted(self.data[y].astype(str)),axid=pax,marker='o')
            elif ptctext == 'Histogram':
                xaxis = self.HistogramXAxisHeader.currentText()
                if xaxis:
                    self.data.sort_values(xaxis,inplace=True)
                    bins = self.HistogramBins.value()
                    self.make_histogram(xaxis,pltr,pax,bins)
            elif ptctext == 'Bar':
                pass
        self.parent.Plot_All(pltr)
    
    def populate_edit_options(self):
        AllItems = [self.PlotTypeCombo.itemText(i) for i in range(self.PlotTypeCombo.count())]
        headers = sorted(list(self.data))
        for ptctext in AllItems:
            if ptctext == 'Line Plot':
                self.LineXAxisHeader.addItem('')
                for header in headers:
                    if self.data[header].dtype.kind not in ['S','O','U']:
                        self.LineYAxisHeaders.addItem(header)
                        self.LineXAxisHeader.addItem(header)
                self.LineXAxisHeader.setCurrentIndex(-1)
            elif ptctext == 'Scatter':
                self.ScatterXAxisHeader.addItem('')
                for header in headers:
                    if self.data[header].dtype.kind not in ['S','O','U']:
                        self.ScatterYAxisHeaders.addItem(header)
                        self.ScatterXAxisHeader.addItem(header)
                self.ScatterXAxisHeader.setCurrentIndex(-1)
            elif ptctext == 'Pie':
                self.PieXAxisHeader.addItem('')
                self.PieXAxisHeader.addItems(headers)
                self.PieXAxisHeader.setCurrentIndex(-1)
            elif ptctext == 'Timeline':
                self.TimelineXAxisHeader.addItem('')
                self.TimelineXAxisHeader.addItems(headers)
                self.TimelineYAxisHeaders.addItems(headers)
                self.TimelineXAxisHeader.setCurrentIndex(-1)
            elif ptctext == 'Histogram':
                self.HistogramXAxisHeader.addItem('')
                self.HistogramXAxisHeader.addItems(headers)
                self.HistogramXAxisHeader.setCurrentIndex(-1)
            elif ptctext == 'Bar':
                self.BarChartXAxisHeader.addItem('')
                for header in headers:
                    if self.data[header].dtype.kind not in ['S','O','U']:
                        self.BarChartXAxisHeader.addItem(header)
                        self.BarChartYAxisHeaders.addItem(header)
                self.BarChartXAxisHeader.setCurrentIndex(-1)
        
            
    def closeEvent(self,event):
        self.parent.show_options(False)


if __name__ == '__main__':
    dic = {'this':np.random.randint(0,50,50),'that':np.random.randint(0,500,50)}
    data = pd.DataFrame(dic)
    app = Widgets.QApplication(sys.argv)
    widget = PlotWidget(None,data,edit=True)
    widget.show()
    app.exec_()
    sys.exit(0)