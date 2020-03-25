# -*- coding: utf-8 -*-
"""
Created on Wed Sep 11 18:07:25 2019

@author: Jordan
"""
import os
import sys

import matplotlib.pyplot as plt
import matplotlib
import PyQt5.QtWidgets as Widgets
import PyQt5.QtGui as Gui
import PyQt5.QtCore as Core
from collections import OrderedDict
import numpy as np
import struct
import binascii
from six import string_types
plt.rcParams['toolbar'] = 'toolmanager'

if not hasattr(sys, 'frozen'):
    RELATIVE_LIB_PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    if __name__ == '__main__':
        sys.path.append(RELATIVE_LIB_PATH)
        sys.path.pop(0)
else:
    RELATIVE_LIB_PATH = os.path.dirname(os.path.dirname(sys.executable))

from PlotH5.mpltools import mplDefaults as mpld
from PlotH5.mpltools import mplUtils as mplu

def update_legend(axes,label,oldlabel,symbol=''):
    '''
    This function will update the legend by finding the old label in the legend
    and replacing it with the new label.
    '''
    legend_handle_labels = axes.properties()['legend_handle_labels']
    for lhl in legend_handle_labels:
        handle_list =  lhl[-1]
        for i,handle in enumerate(handle_list):
            if handle == oldlabel:
                handle_list[i] = label

class DoubleTupleWidget(Widgets.QWidget):
    def __init__(self,origvalue,mainlabel,labels,parent=None,**kwargs):
        super(DoubleTupleWidget,self).__init__(parent)
        
        if not isinstance(origvalue,(tuple,list)):
            print('this is not an accepted iterable')
        if len(origvalue) != len(labels):
            print(origvalue,labels)
            print('the iterable of values was not equal to the number of labels given')
            
        self.layout = Widgets.QGridLayout()
        self.setLayout(self.layout)
        
        self.Label = Widgets.QLabel(mainlabel)
        self.args = []
        for i,val in enumerate(origvalue):
            label = Widgets.QLabel(labels[i])
            widget = Widgets.QLineEdit(str(val))
            widget.setValidator(Gui.QDoubleValidator())
            self.args.append(widget)
            self.layout.addWidget(label,i,0)
            self.layout.addWidget(widget,i,1)

def makeRGBAfromReturn(cname,alpha,**kwargs):
    '''
    Function creates an rgba value from a named color by looking up
    the color name in a dictionary and returning the rgb value.  And appends on
    the alpha value as a float.
    
    Input:
        cname - color name (must be in the mpl color names found in mplDefaults)
        alpha - float (0 - 1) opaqueness of the color
    Kwargs:
        N/A
    Return:
        returns the rgba tuple
    '''
    rgb = mpld.NametoRGB[cname]
    rgba = tuple(rgb,) + tuple([float(alpha)])
    return rgba

class RGBAWidget(Widgets.QWidget):
    def __init__(self,origvalue,parent=None,**kwargs):
        super(RGBAWidget,self).__init__(parent)
        self.makeAlpha = kwargs.get('makeAlpha',True)
        self.alphaval = kwargs.get('alphaval','1.0')
        if not self.alphaval:
            self.alphaval = '1.0'
        if not isinstance(self.alphaval,string_types):
            self.alphaval = str(self.alphaval)
        #This is a named color
        if isinstance(origvalue,string_types) and '#' not in origvalue and isinstance(eval('origvalue'),string_types):        
            self.color_name = mplu.get_closest_name_name(origvalue)
        #This is string tuple.. should never come here
        elif (isinstance(origvalue, string_types) and '#' not in origvalue and isinstance(eval('origvalue'),tuple)) or isinstance(origvalue,tuple):
            if isinstance(origvalue, string_types):
                origvalue = eval(origvalue)
            if len(origvalue) == 4:
                self.alphaval = str(origvalue[-1])
                origvalue = origvalue[:-1]
            self.color_name = mplu.get_cloeset_name_rgb(origvalue)
        elif isinstance(origvalue, string_types):
            origvalue = mplu.convert_hex_to_rgb(origvalue)
            self.color_name = mplu.get_cloeset_name_rgb(origvalue)

        self.layout = Widgets.QGridLayout()
        self.setLayout(self.layout)

        self.ColorCombo = self.buildCombo(mpld.NametoRGB.keys(),self.color_name)
        self.layout.addWidget(self.ColorCombo,0,0)
        if self.makeAlpha:
            self.layout.addWidget(Widgets.QLabel('Alpha'),1,0)
            self.AlphaLine = Widgets.QLineEdit()
            self.AlphaLine.setReadOnly(False)
            self.AlphaLine.setValidator(Gui.QDoubleValidator())
            self.layout.addWidget(self.AlphaLine)
            self.AlphaLine.setText(self.alphaval)

    def buildCombo(self,items,origval):
        print(origval)
        widget = Widgets.QComboBox()
        widget.addItems(items)
        index = widget.findText(origval)
        widget.setCurrentIndex(index)
        return widget

class TextOptions(Widgets.QDialog):
    def __init__(self,artist,parent=None):
        super(TextOptions,self).__init__(parent)
        self.parent = parent
        self.artist = artist
        self.layout = Widgets.QGridLayout()
        self.setLayout(self.layout)
        self.setWindowTitle('Text options')

        self.setupTextOptions()

        self.Ok = Widgets.QPushButton('Ok')
        self.Cancel = Widgets.QPushButton('Cancel')
        self.layout.addWidget(self.Ok)
        self.layout.addWidget(self.Cancel)
        self.makeConnections()

    def makeConnections(self):
        self.Ok.clicked.connect(lambda trash:self.Accept())
        self.Cancel.clicked.connect(lambda trash:self.Reject())

    def buildCombo(self,name,items,origval):
        self.widgets[name] = Widgets.QComboBox()
        self.widgets[name].addItems(items)
        index = self.widgets[name].findText(origval)
        self.widgets[name].setCurrentIndex(index)

    def setupTextOptions(self):
        self.widgets = OrderedDict()
        self.widgets['Text'] = Widgets.QLineEdit(self.artist.get_text())
        self.widgets['Position'] = DoubleTupleWidget(self.artist.get_position(),'Position',['X:','Y:'])
        self.widgets['Text Color'] = RGBAWidget(self.artist.get_color())
        self.widgets['Text Size'] = Widgets.QLineEdit(str(self.artist.get_fontsize()))
        self.widgets['Text Size'].setValidator(Gui.QDoubleValidator())
        self.widgets['Text Font'] = Widgets.QComboBox()
        self.widgets['Text Font'].addItems(['impact','dejavu sans'])

        for key in self.widgets:
            self.layout.addWidget(Widgets.QLabel(key))
            self.layout.addWidget(self.widgets[key])


    def Accept(self):
        #Just to make sure it is still clickable when user stupidly sets it to nothing and hits okay
        if not self.widgets['Text'].text():
            self.widgets['Text'].setText(' ')
        self.artist.set_text(self.widgets['Text'].text())
        self.artist.set_color(mpld.NametoRGB[self.widgets['Text Color'].ColorCombo.currentText()])
        self.artist.set_fontsize(self.widgets['Text Size'].text())
        self.artist.set_fontname(self.widgets['Text Font'].currentText())
        self.artist.set_position(tuple([float(x.text()) for x in self.widgets['Position'].args]))
        self.artist.figure.canvas.draw()
        self.close()

    def Reject(self):
        self.close()

class CollectionsOptions(Widgets.QDialog):
    def __init__(self,artist,legend,parent=None):
        super(CollectionsOptions,self).__init__(parent)
        self.parent = parent
        self.artist = artist
        self.layout = Widgets.QGridLayout()
        self.setLayout(self.layout)
        self.setWindowTitle('Scatter Options')

        self.hascbar = self.determineColorbar()

        self.setupLineOptions()

        self.Ok = Widgets.QPushButton('Ok')
        self.Cancel = Widgets.QPushButton('Cancel')
        self.layout.addWidget(self.Ok)
        self.layout.addWidget(self.Cancel)
        self.makeConnections()
        self.legline = ''

        for line in legend.get_lines():
            if line.get_label() == self.artist.get_label():
                self.legline = line
                break

    def makeConnections(self):
        self.Ok.clicked.connect(lambda trash:self.Accept())
        self.Cancel.clicked.connect(lambda trash:self.Reject())

    def determineColorbar(self):
        #TODO Most likely this will work.. unless all your values are the same with the colorbar
        colors = self.artist.get_facecolor()
        if len(colors) == 1:
            return False
        else:
            return True


    def buildCombo(self,name,items,origval):
        self.widgets[name] = Widgets.QComboBox()
        self.widgets[name].addItems(items)
        index = self.widgets[name].findText(origval)
        self.widgets[name].setCurrentIndex(index)

    def setupLineOptions(self):
        self.widgets = OrderedDict()

        if not self.hascbar:
            self.widgets['Marker Face Color'] = RGBAWidget(tuple(self.artist.get_facecolor()[0]))
            self.widgets['Marker Edge Color'] = RGBAWidget(tuple(self.artist.get_edgecolor()[0]))
        else:
            self.buildCombo('Color Map',mpld.cmaps,self.artist.get_cmap().name)
        self.buildCombo('Marker', ['']+list(mpld.marker_to_array.keys()), mplu.determineMarker(self.artist))
        self.widgets['Marker Size'] = Widgets.QLineEdit(str(self.artist.get_sizes()[0]))
        self.widgets['Marker Size'].setValidator(Gui.QDoubleValidator())

        self.widgets['Line Label'] = Widgets.QLineEdit(self.artist.get_label())

        for key in self.widgets:
            self.layout.addWidget(Widgets.QLabel(key))
            self.layout.addWidget(self.widgets[key])

    def Accept(self):
        #Need to make a color to rgb mapper
        if not self.hascbar:
            self.artist.set_facecolors(np.array(makeRGBAfromReturn(self.widgets['Marker Face Color'].ColorCombo.currentText(),
                                                                   self.widgets['Marker Face Color'].AlphaLine.text())))
            self.artist.set_edgecolors(np.array(makeRGBAfromReturn(self.widgets['Marker Edge Color'].ColorCombo.currentText(),
                                                                   self.widgets['Marker Edge Color'].AlphaLine.text())))
        else:
            self.artist.set_cmap(matplotlib.cm.get_cmap(self.widgets['Color Map'].currentText()))

        self.artist.set_sizes(np.array([float(self.widgets['Marker Size'].text())]))
        self.artist._paths = (matplotlib.path.Path(mpld.marker_to_array[self.widgets['Marker'].currentText()]),)
        self.artist.set_label(self.widgets['Line Label'].text())

        self.artist.figure.canvas.draw()
        self.close()

    def Reject(self):
        self.close()

class Line2DOptions(Widgets.QDialog):
    def __init__(self,artist,legend,parent=None):
        super(Line2DOptions,self).__init__(parent)
        self.parent = parent
        self.artist = artist
        self.layout = Widgets.QGridLayout()
        self.setLayout(self.layout)
        self.setWindowTitle('2D Line Options')

        self.setupLineOptions()

        self.Ok = Widgets.QPushButton('Ok')
        self.Cancel = Widgets.QPushButton('Cancel')
        self.layout.addWidget(self.Ok)
        self.layout.addWidget(self.Cancel)
        self.makeConnections()
        self.legline = ''

        for line in legend.get_lines():
            if line.get_label() == self.artist.get_label():
                self.legline = line
                break

    def makeConnections(self):
        self.Ok.clicked.connect(lambda trash:self.Accept())
        self.Cancel.clicked.connect(lambda trash:self.Reject())

    def buildCombo(self,name,items,origval):
        self.widgets[name] = Widgets.QComboBox()
        self.widgets[name].addItems(items)
        index = self.widgets[name].findText(origval)
        self.widgets[name].setCurrentIndex(index)

    def setupLineOptions(self):
        self.widgets = OrderedDict()

        self.widgets['Line Color'] = RGBAWidget(self.artist.get_color(),alphaval=self.artist.get_alpha())

        self.buildCombo('Marker',['']+list(mpld.marker_to_array.keys()),self.artist.get_marker())
        self.widgets['Marker Face Color'] = RGBAWidget(self.artist.get_markerfacecolor(),makeAlpha=False)
        self.widgets['Marker Edge Color'] = RGBAWidget(self.artist.get_markeredgecolor(),makeAlpha=False)
        self.widgets['Marker Size'] = Widgets.QLineEdit(str(self.artist.get_markersize()))
        self.widgets['Marker Size'].setValidator(Gui.QDoubleValidator())
        self.widgets['Marker Edge Width'] = Widgets.QLineEdit(str(self.artist.get_markeredgewidth()))
        self.widgets['Marker Edge Width'].setValidator(Gui.QDoubleValidator())

        self.buildCombo('Line Style',['-','-.',':','--'],self.artist.get_linestyle())
        self.widgets['Line Width'] = Widgets.QLineEdit(str(self.artist.get_linewidth()))
        self.widgets['Line Width'].setValidator(Gui.QDoubleValidator())

        self.widgets['Line Label'] = Widgets.QLineEdit(self.artist.get_label())

        for key in self.widgets:
            self.layout.addWidget(Widgets.QLabel(key))
            self.layout.addWidget(self.widgets[key])

    def Accept(self):
        self.artist.set_color(mpld.NametoHex[self.widgets['Line Color'].ColorCombo.currentText()])
        self.artist.set_alpha(float(self.widgets['Line Color'].AlphaLine.text()))
        if self.legline:
            self.legline.set_color(mpld.NametoHex[self.widgets['Line Color'].ColorCombo.currentText()])
            self.legline.set_alpha(float(self.widgets['Line Color'].AlphaLine.text()))

        self.artist.set_marker(self.widgets['Marker'].currentText())
        self.artist.set_markerfacecolor(mpld.NametoRGB[self.widgets['Marker Face Color'].ColorCombo.currentText()])
        self.artist.set_markeredgecolor(mpld.NametoRGB[self.widgets['Marker Edge Color'].ColorCombo.currentText()])
        self.artist.set_markersize(self.widgets['Marker Size'].text())
        self.artist.set_markeredgewidth(self.widgets['Marker Edge Width'].text())
        if self.legline:
            self.legline.set_marker(self.widgets['Marker'].currentText())
            self.legline.set_markerfacecolor(mpld.NametoRGB[self.widgets['Marker Face Color'].ColorCombo.currentText()])
            self.legline.set_markeredgecolor(mpld.NametoRGB[self.widgets['Marker Edge Color'].ColorCombo.currentText()])
            self.legline.set_markersize(self.widgets['Marker Size'].text())
            self.legline.set_markeredgewidth(self.widgets['Marker Edge Width'].text())

        self.artist.set_linestyle(self.widgets['Line Style'].currentText())
        self.artist.set_linewidth(self.widgets['Line Width'].text())
        if self.legline:
            self.legline.set_linestyle(self.widgets['Line Style'].currentText())
            self.legline.set_linewidth(self.widgets['Line Width'].text())

        self.artist.set_label(self.widgets['Line Label'].text())
        if self.legline:
            self.legline.set_label(self.widgets['Line Label'].text())

        self.artist.figure.canvas.draw()
        self.close()

    def Reject(self):
        self.close()

class PolygonOptions(Widgets.QDialog):
    def __init__(self,artist,parent=None):
        super(PolygonOptions,self).__init__(parent)
        self.parent = parent
        self.artist = artist
        self.layout = Widgets.QGridLayout()
        self.setLayout(self.layout)
        self.setWindowTitle('Polygon Options')

        self.hascbar = self.determineColorbar()

        self.setupLineOptions()

        self.Ok = Widgets.QPushButton('Ok')
        self.Cancel = Widgets.QPushButton('Cancel')
        self.layout.addWidget(self.Ok)
        self.layout.addWidget(self.Cancel)
        self.makeConnections()

    def makeConnections(self):
        self.Ok.clicked.connect(lambda trash:self.Accept())
        self.Cancel.clicked.connect(lambda trash:self.Reject())

    def determineColorbar(self):
        #TODO Most likely this will work.. unless all your values are the same with the colorbar
        colors = self.artist.get_facecolor()
        if len(colors) == 1:
            return False
        else:
            return True

    def buildCombo(self,name,items,origval):
        self.widgets[name] = Widgets.QComboBox()
        self.widgets[name].addItems(items)
        index = self.widgets[name].findText(origval)
        self.widgets[name].setCurrentIndex(index)

    def setupLineOptions(self):
        self.widgets = OrderedDict()

        if not self.hascbar:
            self.widgets['Marker Face Color'] = RGBAWidget(tuple(self.artist.get_facecolor()[0]))
            self.widgets['Marker Edge Color'] = RGBAWidget(tuple(self.artist.get_edgecolor()[0]))
        else:
            self.buildCombo('Color Map',mpld.cmaps,self.artist.get_cmap().name)

        for key in self.widgets:
            self.layout.addWidget(Widgets.QLabel(key))
            self.layout.addWidget(self.widgets[key])

    def Accept(self):
        #Need to make a color to rgb mapper
        if not self.hascbar:
            self.artist.set_facecolor(makeRGBAfromReturn(self.widgets['Marker Face Color'].ColorCombo.currentText(),
                                                                   self.widgets['Marker Face Color'].AlphaLine.text()))
            self.artist.set_edgecolor(makeRGBAfromReturn(self.widgets['Marker Edge Color'].ColorCombo.currentText(),
                                                                   self.widgets['Marker Edge Color'].AlphaLine.text()))
        else:
            self.artist.set_cmap(matplotlib.cm.get_cmap(self.widgets['Color Map'].currentText()))

        self.artist.figure.canvas.draw()
        self.close()

    def Reject(self):
        self.close()
        
class RectangleOptions(Widgets.QDialog):
    def __init__(self,artist,parent=None):
        super(RectangleOptions,self).__init__(parent)
        self.artist = artist
        self.parent = parent


class Editing_Picker(object):
    def __init__(self,*args,**kwargs):
        self.ann_list = []

    def on_pick(self,event):
        if event.mouseevent.button == 1:
            if isinstance(event.artist,matplotlib.text.Text):
                text = event.artist
                dialog = TextOptions(text)
                dialog.exec_()

            elif isinstance(event.artist,matplotlib.lines.Line2D):
                line = event.artist
                legend = event.artist.axes.legend()
                dialog = Line2DOptions(line,legend)
                dialog.exec_()

            elif isinstance(event.artist,matplotlib.collections.PathCollection):
                collection = event.artist
                legend = event.artist.axes.legend()
                dialog = CollectionsOptions(collection,legend)
                dialog.exec_()

            elif isinstance(event.artist,matplotlib.collections.PolyCollection):
                patch = event.artist
                dialog = PolygonOptions(patch)
                dialog.exec_()
            
            # elif isinstance(event.artist,matplotlib.patches.Rectangle):
            #     patch = event.artist
            #     dialog = RectangleOptions(patch,legend)
            #     dialog.exec()

            else:
                print(event.artist)
        elif event.mouseevent.button == 2:
            print(event.offsetTop,event.offsetLeft,'this')
            try:
                line = event.artist
                xdata = line.get_xdata()
                ydata = line.get_ydata()
                print(xdata)
                ind = event.ind
                ax = line.axes
                ann = ax.annotate(line.get_label(),(xdata[ind[0]],ydata[ind[0]]))
                ann.set_bbox(dict(color='w'))
                self.ann_list.append(ann)
                line.figure.canvas.draw()
            except:
                pass

    def on_release(self,event):
        for ann in self.ann_list:
            ann.remove()
            self.ann_list.remove(ann)
        event.canvas.draw()


ann_list = []
def on_pick(self,event):
    if event.mouseevent.button == 1:
        if isinstance(event.artist,matplotlib.text.Text):
            text = event.artist
            dialog = TextOptions(text)
            dialog.exec_()

        elif isinstance(event.artist,matplotlib.lines.Line2D):
            line = event.artist
            legend = event.artist.axes.legend()
            dialog = Line2DOptions(line,legend)
            dialog.exec_()

        elif isinstance(event.artist,matplotlib.collections.PathCollection):
            collection = event.artist
            legend = event.artist.axes.legend()
            dialog = CollectionsOptions(collection,legend)
            dialog.exec_()

        elif isinstance(event.artist,matplotlib.collections.PolyCollection):
            patch = event.artist
            dialog = PolygonOptions(patch)
            dialog.exec_()

        else:
            print(event.artist)
    elif event.mouseevent.button == 2:
        try:
            line = event.artist
            xdata = line.get_xdata()
            ydata = line.get_ydata()
            ind = event.ind
            ax = line.axes
            ann = ax.annotate(line.get_label(),(xdata[ind[0]],ydata[ind[0]]))
            ann_list.append(ann)
            line.figure.canvas.draw()
        except:
            pass

def on_release(event):
        for ann in ann_list:
            ann.remove()
            ann_list.remove(ann)
        event.canvas.draw()

if __name__ == '__main__':
    fig,ax = plt.subplots()
    ax.scatter([1,2,3,4],[4,5,6,7],picker=5,label='FUN',c='red',cmap=None)
    sc = ax.scatter([5,6,7,8],[4,5,6,7],picker=5,label='Not Fun',c=[1,2,3,4],cmap=plt.cm.get_cmap('flag'))
    fig.colorbar(sc).set_label('nol',picker=5)
    ax.plot([5,6,10,11],[10,11,12,13],picker=5,label='Not Funy',c='#0000FF')
    patch = matplotlib.patches.Rectangle((9,3), 1, 1, facecolor='yellow')
    ax.add_patch(patch)
    jj = ax.annotate('whhhhhat',(5,5),label='when')
    jj.set_bbox(dict(facecolor='green'))
    ax.text(3,3,'whoooo')
    # ax.bar([1,2,3],[3,4,2])
    ax.stackplot([1,2,3,4],[4,5,6,7],picker=5,color='blue',labels=['what'])
    ax.legend()
    fig.suptitle('what')
    ax.set_ylabel('Yes')
    ax.set_xlabel('No')
    ax.set_title('This is a Plot')
    ax.set_picker(5)
    from PlotH5.mpltools import toolbarUtils
    toolbarUtils.add_Tool(fig, ['Editor','SubplotOptions'])
    
    plt.show()


